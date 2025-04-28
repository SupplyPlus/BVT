from odoo import api, fields, models


class CustomerType(models.Model):
    _name = 'customer.type'
    _description = 'Customer Type'

    name = fields.Char(required=True)
