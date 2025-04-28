from odoo import fields, models,api


class ProductSegment(models.Model):
    _name = 'product.segment'

    name = fields.Char(string="Name")
    arabic_name = fields.Char(string='Arabic Name')
    position = fields.Char(string='Position')
    status = fields.Char(string='Status')
    web_image = fields.Binary(string='Image')

    def action_product_segment_api_call(self):
        """Api call wizard from product segment model"""
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
                    'default_segment_ids': record_ids,
                    'default_is_segment': True
                }}

