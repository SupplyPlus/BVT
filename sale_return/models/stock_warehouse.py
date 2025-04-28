from odoo import models, fields, api, _


class Stock(models.Model):
    _inherit = 'stock.warehouse'

    return_steps = fields.Selection([('step_one', 'Return goods directly (1 step)'),
                                     ('step_two', 'Return goods in output and then stock (2 steps)'),
                                     ('step_three', 'Return goods in output, then quality and then stock (3 steps)')],
                                    'Return Shipments',
                                    default='step_one')

    return_route_id = fields.Many2one('stock.route', 'Return Route', ondelete='restrict')

    return_type_id = fields.Many2one('stock.picking.type', 'Return Type', check_company=True)

    # wh__return_input_stock_loc_id = fields.Many2one('stock.location', 'Input Location', check_company=True)


    def _get_routes_values(self):
        res = super(Stock, self)._get_routes_values()
        res['return_route_id'] = {
                'routing_key': self.return_steps,
                'depends': ['return_steps'],
                'route_update_values': {
                    'name': self._format_routename(route_type=self.return_steps),
                    'active': self.active,
                },
                'route_create_values': {
                    'product_categ_selectable': True,
                    'warehouse_selectable': True,
                    'product_selectable': False,
                    'company_id': self.company_id.id,
                    'sequence': 11,
                },
                'rules_values': {
                    'active': True,
                    'procure_method': 'make_to_order',
                    'propagate_cancel': True,
                }
            }
        return res


    def _get_route_name(self, route_type):
        names = {'one_step': _('Receive in 1 step (stock)'), 'two_steps': _('Receive in 2 steps (input + stock)'),
                 'three_steps': _('Receive in 3 steps (input + quality + stock)'), 'crossdock': _('Cross-Dock'),
                 'ship_only': _('Deliver in 1 step (ship)'), 'pick_ship': _('Deliver in 2 steps (pick + ship)'),
                 'pick_pack_ship': _('Deliver in 3 steps (pick + pack + ship)'),
                 'step_one': _('Return in 1 step (stock)'), 'step_two': _('Return in 2 steps (output + stock)'),
                 'step_three': _('Return in 3 steps (output + quality + stock)'), }
        return names[route_type]



    def get_rules_dict(self):
        """ Define the rules source/destination locations, picking_type and
        action needed for each warehouse route configuration.
        """
        customer_loc, supplier_loc = self._get_partner_locations()

        res = super(Stock, self).get_rules_dict()
        for warehouse in self:
            res[warehouse.id].update({
                'step_one': [],
                'step_two': [
                    self.Routing(warehouse.wh_input_stock_loc_id, warehouse.lot_stock_id, warehouse.int_type_id,
                                 'pull_push')],
                'step_three': [
                    self.Routing(warehouse.wh_input_stock_loc_id, warehouse.wh_qc_stock_loc_id, warehouse.int_type_id,
                                 'pull_push'),
                    self.Routing(warehouse.wh_qc_stock_loc_id, warehouse.lot_stock_id, warehouse.int_type_id,
                                     'pull_push')],
                })

        return res




    def _get_return_location(self, return_steps):
        return (self.lot_stock_id if return_steps == 'step_one' else self.wh_input_stock_loc_id)

    def _get_picking_type_create_values(self, max_sequence):
        res, max_sequence = super(Stock, self)._get_picking_type_create_values(max_sequence)
        """ When a warehouse is created this method return the values needed in
        order to create the new picking types for this warehouse. Every picking
        type are created at the same time than the warehouse howver they are
        activated or archived depending the delivery_steps or reception_steps.
        """
        re_loc = self._get_return_location(self.return_steps)
        res['return_type_id'] = {
            'name': _('Sales Return'),
            'code': 'incoming',
            'use_create_lots': True,
            'use_existing_lots': False,
            'default_location_src_id': False,
            'sequence': max_sequence + 1,
            'barcode': self.code.replace(" ", "").upper() + "-RETURN",
            'show_reserved': False,
            'sequence_code': 'RE',
            'company_id': self.company_id.id,
        }

        return res, max_sequence

    def _get_picking_type_update_values(self):
        res = super(Stock, self)._get_picking_type_update_values()

        re_loc = self._get_return_location(self.return_steps)
        res['return_type_id'] = {
            'default_location_dest_id': re_loc.id
        }
        return res

    def _get_sequence_values(self):
        res = super(Stock, self)._get_sequence_values()

        res['return_type_id'] = {
            'name': self.name + ' ' + _('Sequence ret'),
            'prefix': self.code + '/RET/', 'padding': 5,
            'company_id': self.company_id.id,
        }
        return res
