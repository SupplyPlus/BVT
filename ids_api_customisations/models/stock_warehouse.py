from odoo import fields, models, api


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    def action_product_template_api_call(self):
        """Api call wizard from stock warehouse model"""
        record_ids = self._context.get('active_ids')
        if record_ids:
            return {
                'name': "Update To App",
                'type': 'ir.actions.act_window',
                'res_model': 'api.call.wizard',
                'target': 'new',
                'view_id': self.env.ref('ids_api_customisations.api_call_wizard_view').id,
                'view_mode': 'form',
                'context': {
                    'default_warehouse_ids': record_ids,
                    'default_is_warehouse': True
                }}
