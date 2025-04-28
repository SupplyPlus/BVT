###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from . import models
from  . import report
from odoo import api, SUPERUSER_ID




def _create_warehouse_return_data(cr, registry):
    """ This hook is used to add a default manufacture_pull_id, manufacture
    picking_type on every warehouse. It is necessary if the mrp module is
    installed after some warehouses were already created.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    warehouse_ids = env['stock.warehouse'].search([])
    warehouse_ids.update({'return_steps': 'step_one'})