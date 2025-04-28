from odoo import api,fields,models


class Partner(models.Model):
    _inherit = "res.partner"

    sale_rep_id = fields.Many2one('res.partner', string="Partner")