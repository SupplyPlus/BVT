from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        company = self.env.company.id
        return_type_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return_type = return_type_ids.return_type_id.id and return_type_ids.return_type_id.id or False
        res.update({
            'return_type': return_type
        })
        return res

    return_type = fields.Many2one('stock.picking.type')

    @api.onchange('return_type', 'warehouse_id')
    def get_return_type(self):
        self.return_type = self.warehouse_id.return_type_id.id

    def _get_return(self):
        for rec in self:
            rec.return_count = self.env['sale.order'].search_count([('reference_id', '=', rec.id)])

    is_return = fields.Boolean(
        string='Is Return',
    )
    is_missing = fields.Boolean(string="Is Missing", )
    reference_id = fields.Many2one(comodel_name="sale.order", string="Reference")
    state_return = fields.Selection([
        ('draft', 'Draft Return'),
        ('sent', 'Sent Return'),
        ('sale', 'Sale Return'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')],
        string='Sale Return Status',
        compute='_compute_state_return',
    )
    return_count = fields.Integer(string='Return Count', compute='_get_return', readonly=True)

    @api.onchange('is_missing', 'partner_id')
    def onchange_is_missing(self):
        if self.is_missing == True:
            if self.partner_id:
                return {'domain': {
                    'reference_id': [('partner_id', '=', self.partner_id.id), ('state', 'in', ['sale', 'done']),
                                     ('is_return', '=', False)]}}

    @api.depends('state')
    def _compute_state_return(self):
        self.state_return = self.state

    @api.model
    def create(self, vals):
        if vals.get('is_return') and 'name' not in vals:
            vals['name'] = self.env['ir.sequence'].search(
                [('company_id', '=', self.env.user.company_id.id)]).next_by_code('return')
        return super().create(vals)

    @api.onchange('reference_id')
    def _onchange_reference_id(self):
        if self.reference_id:
            line_val = []
            for line in self.reference_id.order_line:
                line_vals = self.env['sale.order.line'].sudo().search_read([('id', '=', line.id)])
                for val in line_vals:
                    del val['id']
                    del val['order_id']
                    del val['create_uid']
                    del val['create_date']
                    del val['write_uid']
                    del val['write_date']
                    del val['__last_update']
                    del val['invoice_lines']
                    del val['invoice_status']
                    del val['qty_delivered']
                    del val['qty_to_invoice']
                    del val['qty_invoiced']
                    del val['move_ids']
                    del val['qty_returned']
                    # del val['margin']
                    val.update({'is_return': True, 'price_subtotal': -val['price_subtotal']})
                    line_val.append((0, 0, val))
            self.order_line = [(5, 0, 0)]
            self.order_line = line_val
            self.warehouse_id = self.reference_id.warehouse_id.id
            self.analytic_account_id = self.reference_id.analytic_account_id.id

    def _create_invoices(self, grouped=False, final=False):
        def recompute_origin(invoice):
            sale_names = list(set(
                s.order_id.name
                for i in invoice.invoice_line_ids
                for s in i.sale_line_ids))
            invoice.invoice_origin = ', '.join(sale_names)

        invoice_ids = super()._create_invoices(grouped, final)
        for invoice in self.env['account.move'].search([('id', 'in', invoice_ids.ids)]):
            if invoice.amount_total != 0:
                if self.is_return:
                    invoice.action_switch_invoice_into_refund_credit_note()
                continue
            new_invoice = invoice.copy({
                'move_type': 'out_refund',
                'invoice_line_ids': False})
            for line in invoice.invoice_line_ids:
                if line.quantity > 0:
                    continue
                line.write({
                    'move_id': new_invoice.id,
                    'quantity': line.quantity * -1,
                    # 'product_uom_id':line.product_uom_id.id,
                })
            for invoice in [new_invoice, invoice]:
                recompute_origin(invoice)
                # invoice.compute_taxes()
            if new_invoice.amount_total == 0:
                new_invoice.unlink()
            else:
                # invoice_ids.append(new_invoice.id)
                invoice_ids |= new_invoice

        return invoice_ids

    def _get_tax_amount_by_group(self):
        self.ensure_one()
        if not self.is_return:
            return super()._get_tax_amount_by_group()
        res = {}
        for line in self.order_line:
            price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
            qty = (line.product_uom_qty * -1) + line.qty_change
            taxes = line.tax_id.compute_all(
                price_reduce, quantity=qty,
                product=line.product_id,
                partner=self.partner_shipping_id)['taxes']
            for tax in line.tax_id:
                group = tax.tax_group_id
                res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                for t in taxes:
                    tax_ids = tax.children_tax_ids.ids
                    if t['id'] == tax.id or t['id'] in tax_ids:
                        res[group]['amount'] += t['amount']
                        res[group]['base'] += t['base']
        res = sorted(res.items(), key=lambda l: l[0].sequence)
        res = [
            (l[0].name, l[1]['amount'], l[1]['base'], len(res)) for l in res]
        return res

    def action_view_return(self):
        return {
            'name': _('Return'),
            # 'view_type': 'tree',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('reference_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def _get_destination_location(self):
        self.ensure_one()
        return self.return_type.default_location_dest_id.id

    def action_confirm(self):
        # self._create_picking()
        res = super(SaleOrder, self).action_confirm()
        if self.is_return:
            self._create_picking()
            self.state_return = 'sale'
            # self.write({"state_return": 'sale'})
            return True
        return res

    @api.model
    def _create_picking(self):
        move_list = []
        for rec in self.order_line:
            move_vals = {
                'name': rec.product_id.name,
                'product_id': rec.product_id.id,
                'product_uom_qty': rec.product_uom_qty,
                'product_uom': rec.product_uom.id,
                'location_id': self.partner_id.property_stock_customer.id,
                'location_dest_id': rec.location_id.id,
                'sale_line_id': rec.id
            }
            move_list.append((0, 0, move_vals))
        picking_vals = {
            'picking_type_id': self.return_type.id,
            'partner_id': self.partner_id.id,
            'user_id': False,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_customer.id,
            'company_id': self.company_id.id,
            'move_ids_without_package': move_list,
        }
        picking = self.env['stock.picking'].create(picking_vals)
        picking.action_assign()

        self.picking_ids = picking
        return picking


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        for line in self:
            if line.order_id.is_return:
                continue
            else:
                return super(SaleOrderLine, self)._action_launch_stock_rule(previous_product_uom_qty)
