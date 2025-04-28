from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    return_type = fields.Many2one('stock.picking.type')

    is_return = fields.Boolean(
        related='order_id.is_return',
        string='Is Return',
    )
    qty_changed = fields.Float(
        compute='_get_to_invoice_qty',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Changed', compute_sudo=True
    )
    qty_change = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        string='Change',
    )
    qty_changed_to_invoice = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_get_to_invoice_qty',
        string='Change to invoice', compute_sudo=True,store=True
    )
    qty_changed_invoiced = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_get_invoice_qty',
        string='Change invoiced', compute_sudo=True, store=True
    )
    qty_returned = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_get_to_invoice_qty',
        string='Returned', compute_sudo=True, default=0.0,store=True
    )
    # qty_returned = fields.Float(
    #     digits=dp.get_precision('Product Unit of Measure'),
    #     compute='_get_to_invoice_qty',
    #     string='Returned',
    # )
    qty_returned_to_invoice = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_get_invoice_qty',
        string='Returned to invoice', compute_sudo=True
    )
    qty_returned_invoiced = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_get_invoice_qty',
        string='Invoiced', default=0.0, compute_sudo=True
    )
    location_id = fields.Many2one(
        comodel_name='stock.location',
        domain='[("usage", "=", "internal")]',
        string='Location',
    )

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for line in self:
            if not line.is_return:
                return super()._compute_amount()
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            qty = (line.product_uom_qty * -1) + line.qty_change
            taxes = line.tax_id.compute_all(
                price, line.order_id.currency_id, qty, product=line.product_id,
                partner=line.order_id.partner_shipping_id)
            tax_amount = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            line.update({
                'price_tax': qty and tax_amount or 0.,
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded']})

    # @api.depends(
    #     'qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state',
    #     'order_id.picking_ids', 'is_return', 'qty_change')
    # def _get_to_invoice_qty(self):
    #     super()._get_to_invoice_qty()
    #     for line in self:
    #         _logger.info("%s",line.qty_returned)
    #         line.qty_returned = 0
    #         line.qty_changed = 0
    #         line.qty_returned_to_invoice = 0
    #         line.qty_changed_to_invoice = 0
    #         if not line.is_return:
    #             return
    #         if line.product_id.type == 'service':
    #             line.qty_returned = line.product_uom_qty
    #             line.qty_delivered = -line.product_uom_qty
    #             line.qty_changed = line.qty_change
    #         else:
    #             line.qty_returned = sum([
    #                 m.quantity_done for m in line.move_ids
    #                 if m.is_return and m.state == 'done'])
    #             # line.qty_delivered = -sum([
    #             #     m.quantity_done for m in line.move_ids
    #             #     if m.is_return and m.state == 'done'])
    #             line.qty_changed = sum([
    #                 m.quantity_done for m in self.move_ids
    #                 if m.is_change and m.state == 'done'])
    #             if line.move_ids:
    #                 line.qty_returned = line.move_ids[0].product_uom._compute_quantity(line.qty_returned, line.product_uom, rounding_method='HALF-UP')
    #                 line.qty_delivered = -line.qty_returned
    #         line.qty_returned_to_invoice = max(
    #             line.qty_returned - line.qty_returned_invoiced, 0)
    #         # line.qty_invoiced = - line.qty_returned_invoiced
    #         line.qty_changed_to_invoice = max(
    #             line.qty_changed - line.qty_changed_invoiced, 0)
    #         line.qty_to_invoice = line.qty_returned_to_invoice

    @api.depends(
        'qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state',
        'order_id.picking_ids', 'is_return', 'qty_change')
    def _get_to_invoice_qty(self):
        # super()._get_to_invoice_qty()
        for line in self:
            line.qty_returned = 0
            line.qty_changed = 0
            line.qty_returned_to_invoice = 0
            line.qty_changed_to_invoice = 0
            if not line.is_return:
                return
            if line.is_return:
                if line.product_id.type == 'service':
                    line.qty_returned = line.product_uom_qty
    
                    line.qty_changed = line.qty_change
                else:
                    line.qty_returned = sum([
                        m.quantity_done for m in line.move_ids
                        if m.is_return and m.state == 'done'])
                    line.qty_changed = sum([
                        m.quantity_done for m in self.move_ids
                        if m.is_change and m.state == 'done'])
                line.qty_returned_to_invoice = max(
                    line.qty_returned - line.qty_returned_invoiced, 0)
                line.qty_changed_to_invoice = max(
                    line.qty_changed - line.qty_changed_invoiced, 0)
                line.qty_to_invoice = line.qty_returned_to_invoice

    @api.depends(
        'state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice',
        'qty_invoiced', 'qty_changed_invoiced', 'qty_returned_invoiced',
        'qty_change', 'qty_changed_to_invoice')
    def _compute_invoice_status(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')

        def compare(a, b):
            return float_compare(a, b, precision_digits=precision)

        def is_to_invoice(line):
            return not float_is_zero(
                line.qty_to_invoice + line.qty_changed_to_invoice,
                precision_digits=precision)

        def is_upselling(line):
            return (
                    line.state == 'sale' and
                    line.product_id.invoice_policy == 'order' and
                    compare(line.qty_delivered, line.product_uom_qty) == 1)

        def is_invoiced(line):
            return (
                    compare(line.qty_changed_invoiced, line.qty_change) >= 0 and
                    compare(line.qty_returned_invoiced, line.product_uom_qty) >= 0)

        super()._compute_invoice_status()
        for line in self:
            if not line.order_id.is_return:
                continue
            if is_to_invoice(line):
                line.invoice_status = 'to invoice'
            elif is_upselling(line):
                line.invoice_status = 'upselling'
            elif is_invoiced(line):
                line.invoice_status = 'invoiced'
            else:
                line.invoice_status = 'no'

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity')
    def _get_invoice_qty(self):
        def has_return(invoice_line):
            return any(
                [l for l in invoice_line.sale_line_ids if l.is_return])

        for line in self:
            line.qty_invoiced = 0.0
            line.qty_returned_invoiced = 0.0
            line.qty_changed_invoiced = 0.0
            invoice_lines = [
                l for l in line.invoice_lines if l.move_id.state != 'cancel']
            for invoice_line in invoice_lines:
                qty = invoice_line.product_uom_id._compute_quantity(
                    invoice_line.quantity, line.product_uom)
                if invoice_line.move_id.move_type == 'out_invoice':
                    if has_return(invoice_line):
                        if qty < 0:
                            line.qty_returned_invoiced -= qty
                        else:
                            line.qty_changed_invoiced += qty
                    else:
                        line.qty_invoiced += qty
                elif invoice_line.move_id.move_type == 'out_refund':
                    if has_return(invoice_line):
                        if qty > 0:
                            line.qty_returned_invoiced += qty
                            line.qty_invoiced = -qty
                        else:
                            line.qty_changed_invoiced -= qty
                    else:
                        line.qty_invoiced -= qty

    def invoice_line_create_vals(self, move_id, qty):
        self.ensure_one()
        if not self.is_return:
            return super().invoice_line_create_vals(move_id, qty)
        lines = super().invoice_line_create_vals(move_id, qty * -1)
        if self.qty_changed_to_invoice:
            lines += super().invoice_line_create_vals(
                move_id, self.qty_changed_to_invoice)
        return lines

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if self.is_return:
            return {}
        # return super()._onchange_product_id_check_availability()

    @api.onchange('order_id', 'product_id')
    def _onchange_location_id(self):
        self.location_id = (
                self.order_id and
                self.order_id.warehouse_id.lot_stock_id.id or None)

    @api.onchange('qty_change')
    def _onchange_qty_change(self):
        if self.qty_change < 0:
            self.qty_change = 0
        elif self.qty_change > self.product_uom_qty:
            self.qty_change = self.product_uom_qty
            raise UserError(
                _('You can not change more units of returned, at most you '
                  'can return %s') % self.product_uom_qty)
