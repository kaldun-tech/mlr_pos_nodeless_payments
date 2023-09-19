# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import requests
import werkzeug
import time
import json
import hashlib
import hmac
import base64
from datetime import datetime, timezone

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, AccessError



_logger = logging.getLogger(__name__)
TIMEOUT = 10

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    def _get_payment_terminal_selection(self):
        return super()._get_payment_terminal_selection() + [('nodeless', 'Nodeless')]

    # cryptopay server fields
    nodeless_payment_flow = fields.Selection([('payment link','Payment Link'),('direct invoice','Direct Invoice')], string='Nodeless Payment Flow')
    nodeless_selected_crypto = fields.Selection([('lightning','BTC-Lightning'),('onchain','BTC-onchain')], string='Nodeless Selected Cryptocurrency')
    nodeless_store_id = fields.Char(string='Nodeless Store ID')
    def call_nodeless_api(self,payload,api,method,jwt=0):
        try:
            request_url = f"{self.server_url}{api}"
            if jwt == 0:
                headers = {"Authorization": "Bearer %s" % (self.api_key), "Content-Type": "application/json", "Accept": "application/json"}
            if jwt == 1:
                jwt_payload = {"email": self.nowpayments_username,
                               "password": self.nowpayments_password}
                jwt_response = self.call_nodeless_api(jwt_payload, '/v1/auth', 'POST', 0)
                _logger.info(jwt_response.json())
                jwtoken = jwt_response.json()['token']
                headers = {"Authorization": "Bearer %s" % (self.api_key), "Content-Type": "application/json", "Accept": "application/json" + jwtoken}
            _logger.info(f"value of server_url is {request_url} and method is {method} and header is {headers}")
            if method == "GET":
                apiRes=requests.get(request_url,headers=headers)
            elif method == "POST":
                apiRes = requests.post(request_url, data=json.dumps(payload), headers=headers)
            _logger.info(apiRes.status_code)
            _logger.info(apiRes.json())
            return apiRes
        except Exception as e:
            _logger.info("API call failure: %s", e.args)
            raise UserError(_("API call failure: %s", e.args))

    def _test_connection(self):
        _logger.info("called nodeless check connection")
        if self.use_payment_terminal == 'nodeless':
            return self.call_nodeless_api({},"/api/v1/status","GET")
        else:
            return super()._test_connection()

    def nodeless_create_crypto_invoice_payment_link(self, args):
        payload = {
             "amount": args['amount'],
            "currency": "USD",}
        _logger.info(payload)
        server_url = "/api/v1/store/" + self.nodeless_store_id + "/invoice"
        create_invoice_api = self.call_nodeless_api(payload, server_url, 'POST')
        if create_invoice_api.status_code != 201:
            return {"code": create_invoice_api.status_code}
        create_invoice_json = create_invoice_api.json()
        inv_json = {
            "code": 0,
            "invoice_id": create_invoice_json['data'].get('id'),
            "invoice": create_invoice_json['data'].get('checkoutLink'),
            "cryptopay_payment_link": create_invoice_json['data'].get('checkoutLink'),
            "cryptopay_payment_type": 'BTC-',
            "crypto_amt": (create_invoice_json['data'].get('satsAmount')/100000000),}
        return inv_json

    def nodeless_create_crypto_invoice_direct_invoice(self, args,nodeless_selected_crypto):
        payload = {
            "amount": args['amount'],
            "currency": "USD",}
        _logger.info(payload)
        server_url = "/api/v1/store/" + self.nodeless_store_id + "/invoice"
        create_invoice_api = self.call_nodeless_api(payload, server_url, 'POST')
        if create_invoice_api.status_code != 201:
            return {"code": create_invoice_api.status_code}
        create_invoice_json = create_invoice_api.json()
        if self.nodeless_selected_crypto == 'lightning':
            inv_json = {
            "code": 0,
            "invoice_id": create_invoice_json['data'].get('id'),
            "invoice": create_invoice_json['data'].get('lightningInvoice'),
            "cryptopay_payment_link": 'lightning:' + create_invoice_json['data'].get('lightningInvoice'),
            "cryptopay_payment_type": 'BTC-'+ self.nodeless_selected_crypto,
            "crypto_amt": (create_invoice_json['data'].get('satsAmount')/100000000),}
        if self.nodeless_selected_crypto == 'onchain':
            inv_json = {
            "code": 0,
            "invoice_id": create_invoice_json['data'].get('id'),
            "invoice": create_invoice_json['data'].get('lightningInvoice'),
            "cryptopay_payment_link": 'BTC:' + create_invoice_json['data'].get('onchainAddress'),
            "cryptopay_payment_type": 'BTC-'+ self.nodeless_selected_crypto,
            "crypto_amt": (create_invoice_json['data'].get('satsAmount')/100000000),}
        _logger.info(inv_json)
        return inv_json

    @api.model
    def nodeless_create_crypto_invoice(self, args):
        _logger.info(f"Called Nodeless create invoice. Passed args are {args}")
        cryptopay_pm = self.env['pos.payment.method'].search([('id', '=', args['pm_id'])], limit=1)
        if cryptopay_pm.use_payment_terminal != 'nodeless':
            return super().nodeless_create_crypto_invoice(args)
        nodeless_payment_flow = cryptopay_pm['nodeless_payment_flow']
        if nodeless_payment_flow == 'direct invoice':
            nodeless_selected_crypto = cryptopay_pm['nodeless_selected_crypto']
            create_invoice_api = cryptopay_pm.nodeless_create_crypto_invoice_direct_invoice(args,nodeless_selected_crypto)
            return create_invoice_api
        else:
            create_invoice_api = cryptopay_pm.nodeless_create_crypto_invoice_payment_link(args)
            return create_invoice_api

    def nodeless_check_payment_status_payment_link(self, args):
        cryptopay_pm = self.env['pos.payment.method'].search([('id', '=', args['pm_id'])], limit=1)
        if cryptopay_pm.use_payment_terminal != 'nodeless':
            return super().nodeless_check_payment_status(args)
        server_url = "/api/v1/store/" + self.nodeless_store_id + "/invoice/" + args['invoice_id'] + "/status"
        invoice_status_api = cryptopay_pm.call_nodeless_api({}, server_url, 'GET')
        if invoice_status_api.status_code != 200:
            return false
        return invoice_status_api.json()

    def nodeless_check_payment_status_direct_invoice(self, args):
        cryptopay_pm = self.env['pos.payment.method'].search([('id', '=', args['pm_id'])], limit=1)
        if cryptopay_pm.use_payment_terminal != 'nodeless':
            return super().nodeless_check_payment_status(args)
        server_url = "/api/v1/store/" + self.nodeless_store_id + "/invoice/" + args['invoice_id'] + "/status"
        invoice_status_api = cryptopay_pm.call_nodeless_api({}, server_url, 'GET')
        if invoice_status_api.status_code != 200:
            return false
        return invoice_status_api.json()

    @api.model 
    def nodeless_check_payment_status(self, args):
        _logger.info(f"Called Nodeless check payment status. Passed args are {args}")
        cryptopay_pm = self.env['pos.payment.method'].search([('id', '=', args['pm_id'])], limit=1)
        if cryptopay_pm.use_payment_terminal != 'nodeless':
            return super().nodeless_check_payment_status(args)
        if cryptopay_pm.nodeless_payment_flow == 'direct invoice':
            check_payment_api = cryptopay_pm.nodeless_check_payment_status_direct_invoice(args)
            return check_payment_api
        else:
            check_payment_api = cryptopay_pm.nodeless_check_payment_status_payment_link(args)
            return check_payment_api

