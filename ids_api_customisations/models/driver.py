from odoo import fields, models,api


class Driver(models.Model):
    _name = 'driver'

    name = fields.Char(string="Name")
