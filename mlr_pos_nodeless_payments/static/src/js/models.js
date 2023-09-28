odoo.define('pos_nodelesspayment.models', function (require) {
var models = require('point_of_sale.models');
var PaymentNodelessPayment = require('pos_nodelesspayment.payment');

models.register_payment_method('nodeless', PaymentNodelessPayment);
});
