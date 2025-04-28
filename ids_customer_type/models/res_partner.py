from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_type_id = fields.Many2one(
        comodel_name='customer.type',
        string='Customer Type',
        required=False)
