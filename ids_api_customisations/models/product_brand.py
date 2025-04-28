from odoo import fields, models,api


class ProductBrand(models.Model):
    _name = 'product.brand'

    name = fields.Char(string="Name")
    arabic_name = fields.Char(string='Arabic Name')
    segment_ids = fields.Many2many('product.segment', string='Segment')
    position = fields.Char(string='Position')
    status = fields.Char(string='Status')
    web_image = fields.Binary(string='Image')

    def action_product_brand_api_call(self):
        """Api call wizard from product Brand model"""
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
                    'default_brand_ids': record_ids,
                    'default_is_brand': True
                }}

