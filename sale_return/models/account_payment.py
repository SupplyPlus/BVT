from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.constrains("partner_id", "amount")
    def get_validation_partner_and_amount(self):
        for payment in self:
            if not payment.partner_id:
                raise ValidationError("Invalid Customer")
            if payment.amount <= 0:
                raise ValidationError("Invalid Amount")
