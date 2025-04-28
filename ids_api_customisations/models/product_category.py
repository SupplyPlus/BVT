from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    arabic_name = fields.Char(string='Arabic Name')
    position = fields.Char(string='Position')
    status = fields.Char(string='Status')
    web_image = fields.Binary(string='Image')

    def action_product_category_api_call(self):
        """Api call wizard from product category model"""
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
                    'default_category_ids': record_ids,
                    'default_is_category': True
                }}
