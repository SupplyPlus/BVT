# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class ids_product_custom_category(models.Model):
#     _name = 'ids_product_custom_category.ids_product_custom_category'
#     _description = 'ids_product_custom_category.ids_product_custom_category'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
