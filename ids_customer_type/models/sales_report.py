from odoo import api, fields, models


class SalesReport(models.Model):
    _inherit = 'sale.report'

    partner_type_id = fields.Many2one(
        comodel_name='customer.type',
        string='Customer Type',
        required=False)

    def _select_sale(self):
        res = super(SalesReport, self)._select_sale()
        res += ", s.partner_type_id"
        return res

    # discount = fields.Float('Discount', readonly=True)

    # def _select(self):
    #     res = super(SalesReport, self)._select()
    #     select_str = res + """,sum(l.product_uom_qty / u.factor * u2.factor * cr.rate * l.price_unit * l.discount / 100.0)
    #          as discount"""
    #     return select_str
