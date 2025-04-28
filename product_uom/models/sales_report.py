from odoo import api, fields, models


class SalesReport(models.Model):
    _inherit = 'sale.report'

    po_qty_invoiced = fields.Float(
        string='Po Qty Invoice',
        required=False, readonly=True)
    po_qty = fields.Float(
        string='Po Qty',
        required=False, readonly=True)

    def _select_sale(self):
        res = super(SalesReport, self)._select_sale()
        res += ", CASE WHEN l.product_id IS NOT NULL THEN SUM((l.qty_invoiced / u.factor * u2.factor)/l.po_qty) ELSE 0 END AS  po_qty_invoiced"
        return res
