from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    is_return = fields.Boolean(
        string='Is return',
    )
    is_change = fields.Boolean(
        string='Is return change',
    )

    # def _action_confirm(self, merge=True, merge_into=False):
    #     for move in self:
    #         if not move.sale_line_id:
    #             continue
    #         sale_line = move.sale_line_id
    #         to_change = sale_line.qty_changed - sale_line.qty_change
    #         if not to_change:
    #             continue
    #         return_type = self.picking_type_id.return_picking_type_id
    #         new_move = self.copy({
    #             'is_return': False,
    #             'is_change': True,
    #             'product_uom_qty': self.sale_line_id.qty_change,
    #             'origin_returned_move_id': move.id,
    #             'picking_type_id': return_type.id,
    #             'location_id': return_type.default_location_src_id.id,
    #             'location_dest_id': self.location_id.id})
    #         self |= new_move
    #
    #     return super()._action_confirm(merge, merge_into)
    #
    # def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
    #     res = super(StockMove,self)._prepare_move_line_vals(quantity, reserved_quant)
    #     if self.is_return:
    #         line_id = self.env['sale.order.line'].search([('order_id','=',self.sale_line_id.order_id.reference_id.id),('product_id','=',self.product_id.id)])
    #         if line_id:
    #             move_id = self.env['stock.move'].search([('sale_line_id','=',line_id.id),('product_id','=',res.get('product_id')),('location_dest_id.usage','=','customer'),('quantity_done','=',quantity)])
    #             move_lines_ids = []
    #             if move_id:
    #                 move_line_id = self.env['stock.move.line'].search([('move_id','=',move_id.id)])
    #                 if move_line_id and move_line_id.lot_id:
    #                     res.update({'lot_id':move_line_id.lot_id.id})
    #     return res

