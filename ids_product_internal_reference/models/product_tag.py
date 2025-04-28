from odoo import fields, models


class ProductTag(models.Model):
    _inherit = "product.tag"

    code_prefix = fields.Char(
        string='Code Prefix',
        copy=False
    )