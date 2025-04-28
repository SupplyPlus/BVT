from odoo import api, fields, models


class SalesReport(models.Model):
    _inherit = 'sale.report'

    sales_rep = fields.Many2one(
        comodel_name='sales.repo',
        string='Sales Rep',
        required=False, )

    def _select_sale(self):
        res = super(SalesReport, self)._select_sale()
        res += ", s.sales_rep"
        return res


