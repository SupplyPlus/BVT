from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    arabic_name = fields.Char(string='Arabic Attribute Name')


class ProductAttributeValues(models.Model):
    _inherit = "product.attribute.value"

    arabic_name = fields.Char(string='Arabic Value')

