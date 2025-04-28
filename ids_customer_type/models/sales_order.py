from odoo import api, fields, models


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    partner_type_id = fields.Many2one(
        comodel_name='customer.type',
        string='Customer Type',
        required=False, related="partner_id.partner_type_id", store=True)


