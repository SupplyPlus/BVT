# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class ids_journal_serial(models.Model):
#     _name = 'ids_journal_serial.ids_journal_serial'
#     _description = 'ids_journal_serial.ids_journal_serial'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
