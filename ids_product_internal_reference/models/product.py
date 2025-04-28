from email.policy import default

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        res.product_variant_ids._update_default_code()
        return res

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_created_from_variant_menu = fields.Boolean(
        string='Create From Variant Menu',
        default=False,
        copy=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        products = super(ProductProduct, self).create(vals_list)
        for rec in products:
            if rec.is_created_from_variant_menu:
                rec._update_default_code()
        return products

    def _update_default_code(self):
        """Update the internal reference (default_code) based on segments, category, tags."""
        for product in self:
            if not product.default_code:
                internal_ref = ""
                if product.product_tmpl_id.segment_ids:
                    for seg in product.product_tmpl_id.segment_ids:
                        if seg.code_prefix:
                            seg_sequence = seg.code_prefix
                            internal_ref += seg_sequence
                if product.product_tmpl_id.categ_id:
                    if product.categ_id.code_prefix:
                        category_sequence = product.categ_id.code_prefix
                        internal_ref += category_sequence
                if product.product_tmpl_id.product_tag_ids:
                    for tag in product.product_tmpl_id.product_tag_ids:
                        if tag.code_prefix:
                            tag_sequence = tag.code_prefix
                            internal_ref += tag_sequence
                if internal_ref:
                    internal_ref += self.env['ir.sequence'].next_by_code('internal.reference.code')
                else:
                    internal_ref = self.env['ir.sequence'].next_by_code('internal.reference.code')
                product.default_code = internal_ref


class ProductCategory(models.Model):
    _inherit = "product.category"

    code_prefix = fields.Char(string='Code Prefix')
