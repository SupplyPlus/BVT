from odoo import api, fields, models


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    sales_rep = fields.Many2one(
        comodel_name='sales.repo',
        string='Sales Rep',
        required=False, )

    @api.onchange("partner_id")
    def get_sales_rep(self):
        for order in self:
            order.sales_rep = order.partner_id.sales_rep
