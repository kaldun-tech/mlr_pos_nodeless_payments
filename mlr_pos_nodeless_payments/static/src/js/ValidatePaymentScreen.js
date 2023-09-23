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
            console.log("called validation")
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

                if (api_resp.status == 'new') {
                    console.log("true");
                    line.crypto_payment_status = 'Invoice Paid';
                    return true;
                }
                else{
                console.log("something else");}

            } catch (error) {
                 console.log(error);
                 return false;
             }
            }
          super.validateOrder(isForceValidate);
        }
      };
    // CustomValidatePaymentScreen.template = "point_of_sale.CustomValidatePaymentScreenTemplate";
  
    Registries.Component.extend(PaymentScreen, CustomValidatePaymentScreen);
  
    return CustomValidatePaymentScreen;
  });
  
