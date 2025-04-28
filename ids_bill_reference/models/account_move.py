# -*- coding: utf-8 -*-
from builtins import len

from odoo import models, fields, api
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from itertools import groupby
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import json
import re


class AccountBillReference(models.Model):
    _name = "account.bill.reference"
    _description = "Vendor Bill References"

    name = fields.Char(string='Name', copy=False, readonly=False, store=True, index=True)


class AccountMove(models.Model):
    _inherit = 'account.move'

    ref_ids = fields.Many2many('account.bill.reference', string='Billing Reference', copy=False, tracking=True, )

    @api.onchange("partner_id")
    def get_ref(self):
        for invoice in self:
            invoice.ref = invoice.partner_id.ref
    new_invoice_number = fields.Char(
        string='Invoice Number',
        required=False)
    # @api.constrains('ref_ids', 'partner_id')
    # def _check_ref(self):
    #     for record in self:
    #         for ref in record.ref_ids.ids and record.move_type == 'in_invoice':
    #             bill = self.env['account.move'].search(
    #                 [('ref_ids', 'in', ref), ('partner_id', '=', self.partner_id.id)])
    #             if len(bill) > 1:
    #                 raise ValidationError(_("You can't create 2 bills with the same vendor and reference"))


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    ref_ids = fields.Many2many(related='move_id.ref_ids', string='Billing Reference')
