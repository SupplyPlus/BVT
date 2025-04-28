from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleReport(models.Model):
    _inherit = 'sale.report'
    margin = fields.Float('Margin', groups="ids_access_right.sales_report_margin_group")
