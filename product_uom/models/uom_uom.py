# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from functools import reduce


class UomUom(models.Model):
    _inherit = 'uom.uom'

    uom_product_type = fields.Selection(
        string="UOM Type",
        selection=[
            ('uom_id', 'Unit of Measure'),
            ('uom_po_id', 'Purchase'),
            ('inv_uom_id', 'Storage'),
            ('other', 'Other')
        ],
        copy=True
    )
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', copy=True)
    signed_ratio = fields.Float(string="Signed Ratio")
    main_uom_name = fields.Char(string="Main UOM", related='product_tmpl_id.uom_id.name',store=True,readonly=False)
    active = fields.Boolean(copy=False)
    is_main_uom = fields.Boolean()
    is_create = fields.Boolean('Is Create')

    @api.constrains("name", "product_tmpl_id", "uom_product_type", "category_id")
    def _check_name(self):
        if self._context.get('install_mode'):
            return
        ctx = dict(self._context, active_test=True)
        for rec in self.with_context(ctx):
            uoms = self.with_context(ctx).search([
                ('category_id', '=', rec.category_id.id),
                ('product_tmpl_id', '=', rec.product_tmpl_id.id),
                ('uom_product_type', '!=', 'other'),
                '|',
                ('uom_product_type', '=', rec.uom_product_type),
                ('name', '=', rec.name),
            ])
            if len(uoms) > 1 and not self._context.get('skip_uom_name_validation', False):
                raise UserError(_(
                    'Uom Name must be unique with Unique Category for every product Template.'
                ))

    @api.model
    def create(self, vals):
        if vals.get('signed_ratio'):
            tec_name = 'factor'
            if vals['signed_ratio'] > 1:
                uom_type = 'bigger'
                tec_name = 'factor_inv'
            elif vals['signed_ratio'] < 1:
                uom_type = 'smaller'
            else:
                uom_type = 'reference'
            vals[tec_name] = vals['signed_ratio']
            vals['uom_type'] = uom_type
        if (vals.get('product_tmpl_id') and not vals.get('category_id')) or \
                self._context.get('custom_category_name'):
            template = self.env['product.template'].browse(vals.get('product_tmpl_id'))
            uom = self.search([('product_tmpl_id', '=', vals.get('product_tmpl_id'))], limit=1)
            if uom:
                category = uom.category_id
            else:
                name = "UOM of %s" % template.name
                category = self.env['uom.category'].create({'name': name})
            vals['category_id'] = category.id
        rec = super(UomUom, self).create(vals)
        # rec.is_create = True
        rec.calculate_rounding()
        return rec

    def calculate_rounding(self):
        def get_rounding(number):
            num_count = len(str(number).split('.')[0])
            rounding = 1 / reduce(lambda x, y: x * y, [10] * (num_count + 1))
            return rounding

        for uom in self:
            if uom.signed_ratio and uom.signed_ratio >= 1:
                uom.rounding = get_rounding(uom.signed_ratio)
            elif uom.signed_ratio and uom.signed_ratio < 1 and uom.signed_ratio > 0:
                uom.rounding = get_rounding(1 / uom.signed_ratio)

    def write(self, values):
        if values.get('signed_ratio'):
            for uom in self:
                new_uom = uom.with_context(dict(self._context, skip_uom_name_validation=True)).copy(
                    default={'signed_ratio': values.get('signed_ratio')})
                uom.with_context(dict(self._context, new_uom=new_uom)).active = False
            del values['signed_ratio']
        # if values:
        #     raise ValidationError("You Can Not Edit")
        return super(UomUom, self).write(values)

    def unlink(self):
        if self.filtered(lambda l: l.uom_product_type == 'uom_id'):
            raise ValidationError(_("You Can't Delete Reference Unit of Measure"))
        self.filtered(lambda l: l.uom_product_type != 'uom_id').write({'active': False})
        products = self.mapped('product_tmpl_id')
        for product in products:
            product.uom_po_id = product.get_uom_po_id()
        return True
