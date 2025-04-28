from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Product(models.Model):
    _inherit = 'product.template'

    @api.constrains("default_code")
    def get_unique(self):
        for product in self:
            if product.default_code:
                product_ref = self.env['product.template'].search(
                    [('id', '!=', product.id), ('default_code', '=', product.default_code),
                     ('default_code', '!=', False)])
                if product_ref:
                    raise ValidationError(_("Internal reference Must Be Unique"))


class ProductProduct(models.Model):
    _inherit = 'product.template'

    @api.constrains("default_code")
    def get_unique(self):
        for product in self:
            if product.default_code:
                product_ref = self.env['product.template'].search(
                    [('id', '!=', product.id), ('default_code', '!=', False),
                     ('default_code', '=', product.default_code)])
                if product_ref and product.default_code:
                    raise ValidationError(_("Internal reference Must Be Unique"))
