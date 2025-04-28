from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    app_segment_ids = fields.Many2many(
        comodel_name='app.segment',
        string='App Segments')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    app_segment_ids = fields.Many2many(
        comodel_name='app.segment',
        string='App Segments', related="product_tmpl_id.app_segment_ids", store=True, readonly=False, column1="app1",
        column2="app2", relation="app")
