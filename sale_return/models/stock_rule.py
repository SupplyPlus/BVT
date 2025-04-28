# from odoo import models
#
#
# class StockRule(models.Model):
#     _inherit = 'stock.rule'
#
#     def _get_stock_move_values(
#         self, product_id, product_qty, product_uom, location_id, name, origin,company_id,values):
#         res = super()._get_stock_move_values(
#             product_id, product_qty, product_uom, location_id, name, origin,company_id,values)
#         sale_line_id = values.get('sale_line_id')
#         if not sale_line_id:
#             return res
#         sale_line = self.env['sale.order.line'].browse(sale_line_id)
#         return_type = self.picking_type_id.return_picking_type_id
#         location_dest =  return_type.default_location_dest_id
#         # if sale_line.order_id.reference_id:
#         #     line_id = self.env['sale.order.line'].search([('order_id','=',sale_line.order_id.reference_id.id),('product_id','=',product_id.id)])
#         #     print(line_id,'line_idline_idline_idline_id')
#         #     if line_id:
#         #         move_id = self.env['stock.move'].search([('sale_line_id','=',line_id.id)])
#         #         print(move_id,'2-3-50820358-285 2-=30582-30')
#         #         move_lines_ids = []
#         #         if move_id:
#         #             move_line_id = self.env['stock.move.line'].search([('move_id','=',move_id.id)])
#         #             # move_line_id = self.env['stock.move.line'].search_read([('move_id','=',move_id.id)])
#
#         #             for line_val in move_line_id:
#         #                 # del line_val['id']
#         #                 # del line_val['picking_id']
#         #                 # del line_val['move_id']
#         #                 # del line_val['qty_done']
#         #                 # del line_val['date']
#         #                 # del line_val['location_id']
#         #                 # del line_val['location_dest_id']
#         #                 # del line_val['lots_visible']
#         #                 # del line_val['picking_code']
#         #                 # del line_val['reference']
#         #                 # del line_val['tracking']
#         #                 # del line_val['origin']
#         #                 # del line_val['create_uid']
#         #                 # del line_val['create_date']
#         #                 # del line_val['write_uid']
#         #                 # del line_val['write_date']
#         #                 # del line_val['__last_update']
#         #                 # if line_val.get('lot_id'):
#         #                 #     line_val['lot_id'] = line_val.get('lot_id')[0]
#         #                 # if line_val.get('product_id'):
#         #                 #         line_val['product_id'] = line_val.get('product_id')[0]
#         #                 move_lines_ids.append((0,0,{'product_id':line_val.product_id.id,
#         #                                             'lot_id':line_val.lot_id.id,
#         #                                             'location_id':res['location_dest_id'],
#         #                                             'location_dest_id':location_dest.id,
#         #                                             'product_uom_id':product_uom.id,
#         #                                             'product_uom_qty':line_val.product_uom_qty,
#         #                                             # 'product_qty':line_val.product_qty,
#         #                                             'qty_done':line_val.qty_done,
#         #                                             'picking_id':res.get('picking_id')
#         #                     }))
#                     # ahfnbajh<BAJKBGVjh,zxvgb<JD
#         if sale_line.is_return <= 0:
#             return res
#         res.update({
#             'is_return': True,
#             'picking_type_id': return_type.id,
#             'location_id': res['location_dest_id'],
#             'location_dest_id': location_dest.id,
#             # 'move_line_ids':move_lines_ids
#             })
#         return res
