from odoo import api, fields, models


class AccountMoveLine(models.AbstractModel):
    _inherit = 'account.move.line'

    sales_rep = fields.Many2one('sales.repo', string="Sales Rep", related="move_id.sales_rep", store=True)


class AccountMove(models.AbstractModel):
    _inherit = 'account.move'

    # ref_bill = fields.Char(
    #     string='Ref Bills',
    #     required=False, compute='get_ref_bills', store=True)
    #
    # @api.depends("ref_ids")
    # def get_ref_bills(self):
    #     for move in self:
    #         move.ref_bill = ' , '.join(move.ref_ids.mapped('name'))
