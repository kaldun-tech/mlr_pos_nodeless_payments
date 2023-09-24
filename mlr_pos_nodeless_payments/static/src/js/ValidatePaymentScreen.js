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
            console.log("called nodeless validation");
            if(line.is_crypto_payment && line.payment_method.use_payment_terminal == 'nodeless') {
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

                if (api_resp.status == 'paid') {
                     console.log("valid nodeless transaction");
                     line.crypto_payment_status = 'Invoice Paid';
                     line.set_payment_status('done');
				}
                                else if (api_resp.status == 'new') {
	                                this.showPopup("ErrorPopup", {
       		                                 title: this.env._t("Payment Request Pending"),
               		                         body: this.env._t("Payment Pending, retry after customer confirms"),
                       		        });
                       		        line.set_payment_status('cryptowaiting');
                                }
				else if (api_resp.status == 'expired') {
				        console.log("expired nodeless transaction");
				        this.showPopup("ErrorPopup", {
                                                 title: this.env._t("Payment Request Expired"),
                                                 body: this.env._t("Payment Request expired, retry to send another send request"),
                                        });
				        line.set_payment_status('retry');
				}
				else if (api_resp.status) {
				        console.log("unknown nodeless transaction");
				        this.showPopup("ErrorPopup", {
                                                 title: this.env._t("Payment Request unknown"),
                                                 body: this.env._t("Payment Request unknown, retry to send another send request"),
                                        });
				}}
				catch (error) {
                 console.log(error);
                 return false;
             }}
            }
          super.validateOrder(isForceValidate);
        }
      };
    // CustomValidatePaymentScreen.template = "point_of_sale.CustomValidatePaymentScreenTemplate";
  
    Registries.Component.extend(PaymentScreen, CustomValidatePaymentScreen);
  
    return CustomValidatePaymentScreen;
  });
  
