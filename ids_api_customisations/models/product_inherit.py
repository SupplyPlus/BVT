from odoo import fields, models, api


# product

class Product(models.Model):
    _inherit = 'product.template'

    segment_ids = fields.Many2many('product.segment', string="Segment")
    brand_id = fields.Many2one('product.brand', string="Brand")

    # parent_sku = fields.Char(string="Parent sku")
    product_sku = fields.Char(string="Product sku")
    show_list = fields.Boolean(string="Show list", default=False)

    arabic_name = fields.Char(string='Arabic Name')
    arabic_description = fields.Char(string='Arabic Description')



    def action_product_template_api_call(self):
        """Api call wizard from product Template model"""
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
                    'default_product_temp_ids': record_ids,
                    'default_is_product': True
                }}


class ProductProduct(models.Model):
    _inherit = "product.product"

    # segment_ids = fields.Many2many('product.segment', string="Segment")
    brand_id = fields.Many2one('product.brand', string="Brand")

    parent_sku = fields.Char(string="Parent sku")
    product_sku = fields.Char(string="Product sku")
    show_list = fields.Boolean(string="Show list", default=False)

    arabic_name = fields.Char(string='Arabic Name')
    arabic_description = fields.Char(string='Arabic Description')

    product_image_ids = fields.Many2many('ir.attachment', string="Images")
