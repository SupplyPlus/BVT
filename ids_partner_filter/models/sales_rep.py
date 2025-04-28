from odoo import api, fields, models
class SalesRepo(models.Model):
    _name = 'sales.repo'
    _description = 'Sales Repo'

    name = fields.Char()
    mobile = fields.Char()

