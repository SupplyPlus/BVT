from odoo import fields, models


class ProductSegment(models.Model):
    _inherit = "product.segment"

    code_prefix = fields.Char(
        string='Code Prefix',
        copy=False
    )
