from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    sales_rep = fields.Many2one(
        comodel_name='sales.repo',
        string='Sales Rep',
        required=False)

    # @api.constrains("ref")
    # def get_unique(self):
    #     for customer in self:
    #         if customer.ref:
    #             customer_ref = self.env['res.partner'].search(
    #                 [('id', '!=', customer.id), ('ref', '=', customer.ref), ('ref', '!=', False)])
    #             if customer_ref:
    #                 raise ValidationError(_("Reference Must Be Unique"))
