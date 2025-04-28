# -*- coding: utf-8 -*-

import odoo
from odoo import api, SUPERUSER_ID


def recompute_uom_uom_rounding(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    model = env['uom.uom']
    model.search([]).calculate_rounding()


def migrate(cr, version):
    recompute_uom_uom_rounding(cr)
