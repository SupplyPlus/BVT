# from odoo import api, fields, models, SUPERUSER_ID, _
#
# class Picking(models.Model):
#     _inherit = "stock.picking"
#
#
#     # @api.model
#     # def create(self, vals):
#     # 	# if vals.get('stock_mo'):
#     # 	res = super(Picking,self).create(vals)
#
#     # 	for line in res.move_ids_without_package:
#     # 	return res
#
#     # def action_confirm(self):
#     # 	res = super(Picking,self).action_confirm()
#     #     if self.sale_id.reference_id:
#     #         line_id = self.env['sale.order.line'].search([('order_id','=',self.sale_id.reference_id.id),('product_id','=',product_id.id)])
#     #         if line_id:
#     #             move_id = self.env['stock.move'].search([('sale_line_id','=',line_id.id)])
#     #             move_lines_ids = []
#     #             if move_id:
#     #                 move_line_id = self.env['stock.move.line'].search([('move_id','=',move_id.id)])
#     #                 # move_line_id = self.env['stock.move.line'].search_read([('move_id','=',move_id.id)])
#
#     #                 for line_val in move_line_id:
#     #                     # del line_val['id']
#     #                     # del line_val['picking_id']
#     #                     # del line_val['move_id']
#     #                     # del line_val['qty_done']
#     #                     # del line_val['date']
#     #                     # del line_val['location_id']
#     #                     # del line_val['location_dest_id']
#     #                     # del line_val['lots_visible']
#     #                     # del line_val['picking_code']
#     #                     # del line_val['reference']
#     #                     # del line_val['tracking']
#     #                     # del line_val['origin']
#     #                     # del line_val['create_uid']
#     #                     # del line_val['create_date']
#     #                     # del line_val['write_uid']
#     #                     # del line_val['write_date']
#     #                     # del line_val['__last_update']
#     #                     # if line_val.get('lot_id'):
#     #                     #     line_val['lot_id'] = line_val.get('lot_id')[0]
#     #                     # if line_val.get('product_id'):
#     #                     #         line_val['product_id'] = line_val.get('product_id')[0]
#     #                     move_lines_ids.append((0,0,{'product_id':line_val.product_id.id,
#     #                                                 'lot_id':line_val.lot_id.id,
#     #                                                 'location_id':res['location_dest_id'],
#     #                                                 'location_dest_id':location_dest.id,
#     #                                                 'product_uom_id':product_uom.id,
#     #                                                 'product_uom_qty':line_val.product_uom_qty,
#     #                                                 # 'product_qty':line_val.product_qty,
#     #                                                 'qty_done':line_val.qty_done,
#     #                                                 'picking_id':self.picking_id.id
#     #                         }))