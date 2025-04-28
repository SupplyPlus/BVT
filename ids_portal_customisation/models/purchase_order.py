# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    delivery_date = fields.Datetime('Delivery Date')

    def action_rfq_confirm(self):
        for rec in self:
            rec.sudo().button_confirm()
