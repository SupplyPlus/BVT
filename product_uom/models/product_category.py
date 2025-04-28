from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'



class Brand(models.Model):
    _name = 'brand.brand'
    _description = 'Brand'

    name = fields.Char()
