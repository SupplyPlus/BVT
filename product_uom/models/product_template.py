# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Product(models.Model):
    _inherit = 'product.product'

    # brand_id = fields.Many2one(
    #     comodel_name='brand.brand',
    #     string='Brand',
    #     required=False)

    def get_uom_po_id(self):
        self.ensure_one()
        return self.uom_ids.filtered(lambda u: u.uom_product_type == 'uom_po_id' and u.active) or \
            self.uom_ids.filtered(lambda u: u.uom_product_type == 'inv_uom_id' and u.active) or \
            self.uom_ids.filtered(lambda u: u.uom_product_type == 'uom_id' and u.active) or \
            self.uom_po_id or self.uom_id

    po_uom = fields.Char(
        string='Po Uom',
        required=False, )
    po_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Po Unit',
        required=False, compute="get_purchase_uom")
    po_on_hand_qty = fields.Float(
        string='Po OnHand',
        required=False, compute="get_purchase_uom")
    po_free_to_use = fields.Float(
        string='Po Free To Use',
        required=False, compute="get_purchase_uom")
    po_uom_outgoing = fields.Float(
        string='Po OutGoing',
        required=False, compute="get_purchase_uom")

    @api.depends("product_tmpl_id", "product_tmpl_id.uom_ids", "product_tmpl_id.uom_ids.uom_product_type",
                 "product_tmpl_id.uom_ids.signed_ratio", "outgoing_qty", "qty_available", "free_qty")
    def get_purchase_uom(self):
        for product in self:
            if product.product_tmpl_id.uom_ids and product.product_tmpl_id.uom_ids.filtered(
                    lambda x: x.uom_product_type == 'uom_po_id'):
                purchase_uom_id = product.product_tmpl_id.uom_ids.filtered(
                    lambda x: x.uom_product_type == 'uom_po_id')
                product.po_uom_id = purchase_uom_id[0]
                if purchase_uom_id[0].signed_ratio > 0:
                    product.po_on_hand_qty = product.qty_available / purchase_uom_id[0].signed_ratio
                    product.po_free_to_use = product.free_qty / purchase_uom_id[0].signed_ratio
                    product.po_uom_outgoing = product.outgoing_qty / purchase_uom_id[0].signed_ratio
                else:
                    product.po_on_hand_qty = 0
                    product.po_free_to_use = 0
                    product.po_uom_outgoing = 0
            else:
                product.po_uom_id = False
                product.po_on_hand_qty = 0
                product.po_free_to_use = 0
                product.po_uom_outgoing = 0


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # brand_id = fields.Many2one(
    #     comodel_name='brand.brand',
    #     string='Brand',
    #     required=False)

    def _get_default_uom_name(self):
        return 'PC'

    uom_ids = fields.One2many('uom.uom', 'product_tmpl_id', string='Multi Uom')
    uom_category_id = fields.Many2one('uom.category', related="uom_ids.category_id")

    so_uom_name = fields.Char('Unit of Measure (text)', default=_get_default_uom_name, required=False)
    po_uom_name = fields.Char('PO UOM (text)', default=_get_default_uom_name, required=False)
    storage_uom_name = fields.Char('Storage UOM (text)', default=_get_default_uom_name, required=False)
    po_uom_factor = fields.Float('PO UOM Factor', default=1, required=False)
    storage_uom_factor = fields.Float('Storage UOM Factor', default=1, required=False)
    uom_id = fields.Many2one(default=lambda self: self._get_default_uom_id())
    uom_po_id = fields.Many2one(default=lambda self: self._get_default_uom_id())
    inv_uom_id = fields.Many2one(
        string="Storage UOM", comodel_name='uom.uom',
        compute="_compute_inv_uom", store=True
    )
    inv_uom_name = fields.Char(string="Storage", compute="_compute_inv_uom_name")

    @api.depends('uom_ids.uom_product_type', 'uom_id')
    def _compute_inv_uom_name(self):
        for rec in self:
            inv_uoms = rec.uom_ids.filtered(lambda u: u.uom_product_type == 'inv_uom_id' and u.active) or \
                       rec.uom_ids.filtered(lambda u: u.uom_product_type == 'uom_po_id' and u.active) or \
                       rec.uom_ids.filtered(lambda u: u.uom_product_type == 'uom_id' and u.active)
            rec.inv_uom_name = inv_uoms and inv_uoms[0].name or rec.uom_id.name

    @api.depends('uom_ids.uom_product_type', 'uom_id')
    def _compute_inv_uom(self):
        for rec in self:
            inv_uoms = rec.uom_ids.filtered(lambda u: u.uom_product_type == 'inv_uom_id' and u.active) or \
                       rec.uom_ids.filtered(lambda u: u.uom_product_type == 'uom_po_id' and u.active) or \
                       rec.uom_ids.filtered(lambda u: u.uom_product_type == 'uom_id' and u.active)
            rec.inv_uom_id = inv_uoms and inv_uoms[0].id or rec.uom_id.id

    def _get_default_uom_id(self):
        # return self.env["uom.uom"].search([()], limit=1, order='id').id
        # FIXME: ISLAM: i change this because it raise error on create product
        # return False
        return super(ProductTemplate, self)._get_default_uom_id()

    @api.constrains('uom_id', 'uom_po_id')
    def _check_uom(self):
        """
            if any(
                template.uom_id and template.uom_po_id and
                template.uom_id.category_id != template.uom_po_id.category_id
                for template in self
            ):
                raise ValidationError(_(
                    'The default Unit of Measure and the purchase Unit of Measure must be
                    in the same category.'
                ))
        """
        return True

    @api.constrains('uom_ids')
    def _check_uom_ids(self):
        if not self._context.get('skip_check_uom', False):
            for rec in self:
                if not rec.uom_ids:
                    raise ValidationError(_(
                        'NO UOMs defined for this product please define new uom in UOM Category tab'
                    ))
                if any(not u.signed_ratio for u in rec.uom_ids):
                    raise ValidationError(_('All UOM Categories Must have Ratio'))

    @api.model
    def create(self, vals):
        uom_obj = self.env['uom.uom']
        uom_list = []
        names = []
        uom_vals = {'sale_uom': False, 'po_uom': False, 'other_uom': False}
        uom_category = self.env['uom.category'].create({'name': vals.get('name')})
        bulk_create_uoms = False
        if vals.get('uom_ids'):
            for item in vals.get('uom_ids'):
                if not (isinstance(item, list) and len(item) == 3 and item[0] == item[1] == 0 and isinstance(
                        item[2], dict)):
                    break
                else:
                    item[2].update({'category_id': uom_category.id})
            else:
                bulk_create_uoms = True

        if not bulk_create_uoms:
            defaults = self.default_get(['so_uom_name', 'po_uom_name', 'storage_uom_name'])
            if not vals.get('so_uom_name'):
                vals['so_uom_name'] = defaults.get('so_uom_name')
            if not vals.get('po_uom_name') and not vals.get('so_uom_name'):
                vals['po_uom_name'] = defaults.get('po_uom_name')
            if not vals.get('storage_uom_name') and not vals.get('so_uom_name'):
                vals['storage_uom_name'] = defaults.get('storage_uom_name')
            if vals.get('so_uom_name'):
                names.append(vals['so_uom_name'])
                so_uom = self._create_product_uom(
                    vals['so_uom_name'], uom_category, 1, 'uom_id', True, barcode=vals.get('uom_barcode', False)
                )
                uom_vals['sale_uom'] = so_uom
                uom_obj |= so_uom
            if vals.get('po_uom_name') and vals['po_uom_name'] not in names:
                names.append(vals['po_uom_name'])
                po_uom = self._create_product_uom(
                    vals.get('po_uom_name'), uom_category, vals.get('po_uom_factor'), 'uom_po_id',
                    barcode=vals.get('purchase_barcode', False)
                )
                uom_vals['po_uom'] = po_uom
                uom_obj |= po_uom
            if vals.get('storage_uom_name') and vals['storage_uom_name'] not in names:
                storage_uom = self._create_product_uom(
                    vals.get('storage_uom_name'), uom_category,
                    vals.get('storage_uom_factor'), 'inv_uom_id', barcode=vals.get('storage_barcode', False)
                )
                uom_vals['other_uom'] = storage_uom
                uom_obj |= storage_uom
            uom_list = [(4, uom_id) for uom_id in uom_obj.ids]
            final_uom_vals = self._prepare_uom_vals(uom_vals)
            vals.update(final_uom_vals)
        ctx = dict(self._context, skip_check_uom=True)
        res = super(ProductTemplate, self.with_context(ctx)).create(vals)
        if bulk_create_uoms:
            res.uom_id = res.uom_ids.filtered(lambda u: u.uom_product_type == 'uom_id')
            res.uom_po_id = res.get_uom_po_id()
        if not bulk_create_uoms and uom_list:
            res.uom_ids = uom_list
        uom_category.name = '_'.join([uom_category.name, str(res.id)])
        return res

    def write(self, vals):
        # this changes is added to enable import uom names to update its names and ratio
        if vals.get('so_uom_name') and self.uom_id:
            uom_id = self.uom_ids.filtered(lambda r: r.uom_product_type == 'uom_id')
            uom_id.write({
                'name': vals['so_uom_name'],
                'is_main_uom': True,
            })
        if vals.get('po_uom_name') and vals['po_uom_name']:
            po_uom = self.uom_ids.filtered(lambda r: r.uom_product_type == 'uom_po_id')
            if po_uom:
                po_uom.name = vals['po_uom_name']
            else:
                po_uom = self._create_product_uom(
                    vals.get('po_uom_name'), self.uom_category_id, vals.get('po_uom_factor'), 'uom_po_id',
                    barcode=vals.get('purchase_barcode')
                )
            vals['uom_ids'] = [(4, po_uom.id)]
        # end of changes

        res = super(ProductTemplate, self).write(vals)
        if vals.get('uom_ids'):
            self._update_uoms()
        return res

    def get_uom_po_id(self):
        self.ensure_one()
        return self.uom_ids.filtered(lambda u: u.uom_product_type == 'uom_po_id' and u.active) or \
            self.uom_ids.filtered(lambda u: u.uom_product_type == 'inv_uom_id' and u.active) or \
            self.uom_ids.filtered(lambda u: u.uom_product_type == 'uom_id' and u.active) or \
            self.uom_po_id or self.uom_id

    def _update_uoms(self):
        for rec in self:
            uom_vals = {
                'sale_uom': rec.uom_ids.filtered(lambda u: u.uom_product_type == 'uom_id' and u.active),
                'po_uom': rec.uom_ids.filtered(lambda u: u.uom_product_type == 'uom_po_id' and u.active) or
                          rec.uom_ids.filtered(lambda u: u.uom_product_type == 'inv_uom_id' and u.active) or
                          rec.uom_ids.filtered(lambda u: u.uom_product_type == 'uom_id' and u.active),
                'other_uom': rec.uom_ids.filtered(lambda u: u.uom_product_type == 'other' and u.active),
            }
            final_uom_vals = self._prepare_uom_vals(uom_vals)
            rec.write(final_uom_vals)

    @api.model
    def _prepare_uom_vals(self, vals):
        sale_uom = vals.get('sale_uom')
        po_uom = vals.get('po_uom')
        other_uom = vals.get('other_uom')
        if sale_uom and not po_uom:
            sale_id = sale_uom[0].id
            purchase_id = sale_id
        elif sale_uom and po_uom:
            sale_id = sale_uom[0].id
            purchase_id = po_uom[0].id
        elif not sale_uom and po_uom:
            purchase_id = po_uom[0].id
            sale_id = purchase_id
        else:
            sale_id = other_uom[0].id
            purchase_id = sale_id
        if not po_uom:
            if other_uom:
                purchase_id = other_uom[0].id
        return {
            'uom_id': sale_id,
            'uom_po_id': purchase_id,
        }

    def _create_product_uom(self, name, categ, factor, uom_product_type, is_main_uom=False, barcode=False):
        return self.env['uom.uom'].create({
            'name': name,
            'uom_product_type': uom_product_type,
            'signed_ratio': factor,
            'category_id': categ.id,
            'is_main_uom': is_main_uom,
        })

    @api.model
    def auto_create_uom_ids(self, limit=1000):
        """ auto create uom_ids and uom category : will be used from schedual action """
        products = self.sudo().search([('uom_ids', '=', False)], limit=limit)

        for rec in products:
            uom_category = self.env['uom.category'].create({'name': rec.name})
            name = rec._get_default_uom_name()
            so_uom = self.sudo().env['uom.uom'].create({
                'name': name,
                'category_id': uom_category.id,
                'signed_ratio': 1,
                'uom_product_type': 'uom_id',
                'is_main_uom': True,
                'product_tmpl_id': rec.id,
            })
            rec.write({
                'uom_id': so_uom.id,
                'uom_po_id': so_uom.id,
                'uom_category_id': uom_category.id,
            })
