from odoo import api, fields, models, _


class Partner(models.Model):
    _inherit = 'res.partner'

    responsible_id = fields.Many2one('res.users', string="Responsible", tracking=True)

