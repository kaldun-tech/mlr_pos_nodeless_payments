odoo.define("point_of_sale.CustomValidatePaymentScreen", function (require) {
    "use strict";
    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const Registries = require("point_of_sale.Registries");
    var rpc = require('web.rpc');
  
    const CustomValidatePaymentScreen = (PaymentScreen) =>
      class extends PaymentScreen {
        setup() {
          super.setup();
        }
        async validateOrder(isForceValidate) {
            for (let line of this.paymentLines) {
<<<<<<< HEAD:mlr_pos_nodeless_payments/static/src/js/ValidatePaymentScreen.js
            console.log("called nodeless validation");
            if(line.is_crypto_payment && line.payment_method.use_payment_terminal == 'nodeless') {
=======
            console.log("called validation")
>>>>>>> main:static/src/js/ValidatePaymentScreen.js
            try {
                let order_id = this.env.pos.get_order().uid;
                let api_resp = await rpc.query({
                    model: 'pos.payment.method',
                    method: 'nodeless_check_payment_status',
                    args: [{ invoice_id: line.cryptopay_invoice_id, pm_id: line.payment_method.id, order_id: order_id }],
                }, {
                    silent: true,
                });
                console.log(api_resp);
                console.log(api_resp.status);

<<<<<<< HEAD:mlr_pos_nodeless_payments/static/src/js/ValidatePaymentScreen.js
                if (api_resp.status == 'paid') {
                     console.log("valid nodeless transaction");
                     line.crypto_payment_status = 'Invoice Paid';
                     line.set_payment_status('done');
=======
                if (api_resp.status == 'new') {
                     console.log("true new");
                     line.crypto_payment_status = 'Invoice Paid';
                     line.set_payment_status('done');
                     //this.validateOrder(true);
                     return true;
>>>>>>> main:static/src/js/ValidatePaymentScreen.js
				}
                                else if (api_resp.status == 'new') {
	                                this.showPopup("ErrorPopup", {
       		                                 title: this.env._t("Payment Request Pending"),
               		                         body: this.env._t("Payment Pending, retry after customer confirms"),
                       		        });
<<<<<<< HEAD:mlr_pos_nodeless_payments/static/src/js/ValidatePaymentScreen.js
                       		        line.set_payment_status('cryptowaiting');
                                }
				else if (api_resp.status == 'expired') {
				        console.log("expired nodeless transaction");
=======
                                }
				else if (api_resp.status == 'Expired') {
>>>>>>> main:static/src/js/ValidatePaymentScreen.js
				        this.showPopup("ErrorPopup", {
                                                 title: this.env._t("Payment Request Expired"),
                                                 body: this.env._t("Payment Request expired, retry to send another send request"),
                                        });
<<<<<<< HEAD:mlr_pos_nodeless_payments/static/src/js/ValidatePaymentScreen.js
				        line.set_payment_status('retry');
				}
				else if (api_resp.status) {
				        console.log("unknown nodeless transaction");
				        this.showPopup("ErrorPopup", {
                                                 title: this.env._t("Payment Request unknown"),
                                                 body: this.env._t("Payment Request unknown, retry to send another send request"),
                                        });
=======
>>>>>>> main:static/src/js/ValidatePaymentScreen.js
				}}
				catch (error) {
                 console.log(error);
                 return false;
<<<<<<< HEAD:mlr_pos_nodeless_payments/static/src/js/ValidatePaymentScreen.js
             }}
=======
             }
>>>>>>> main:static/src/js/ValidatePaymentScreen.js
            }
          super.validateOrder(isForceValidate);
        }
      };
    // CustomValidatePaymentScreen.template = "point_of_sale.CustomValidatePaymentScreenTemplate";
  
    Registries.Component.extend(PaymentScreen, CustomValidatePaymentScreen);
  
    return CustomValidatePaymentScreen;
  });
  
