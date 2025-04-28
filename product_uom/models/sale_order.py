from odoo import api, fields, models


class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'

    po_qty = fields.Float(
        string='Po Qty',
        required=False, compute="_compute_product_uom", store=True, default=1)

    @api.depends('product_id', 'product_id.product_tmpl_id.uom_ids', 'product_id.product_tmpl_id.uom_ids.signed_ratio')
    def _compute_product_uom(self):
        for line in self:
            purchase_uom = line.product_id.product_tmpl_id.uom_ids.filtered(lambda x: x.uom_product_type == 'uom_po_id')
            if purchase_uom:
                line.product_uom = purchase_uom[0]
                if purchase_uom[0].signed_ratio > 0:
                    line.po_qty = purchase_uom[0].signed_ratio
                else:
                    line.po_qty = 1
            else:
                line.po_qty = 1
                if not line.product_uom or (line.product_id.uom_id.id != line.product_uom.id):
                    line.product_uom = line.product_id.uom_id
                if not line.product_uom or (line.product_id.uom_id.id != line.product_uom.id):
                    line.product_uom = line.product_id.uom_id
