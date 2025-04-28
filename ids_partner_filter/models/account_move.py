from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    sales_rep = fields.Many2one(
        comodel_name='sales.repo',
        string='Sales Rep',
        required=False, )

    @api.onchange("partner_id")
    def get_sales_rep(self):
        for move in self:
            move.sales_rep = move.partner_id.sales_rep

    @api.onchange("move_type")
    def get_filter(self):
        for move in self:
            if move.move_type == 'out_invoice':
                customers = self.env['res.partner'].search([('customer_rank', '>', 0)])
                return {
                    'domain': {'partner_id': [('id', 'in', customers.ids)]}
                }
            if move.move_type == 'in_invoice':
                vendors = self.env['res.partner'].search([('supplier_rank', '>', 0)])
                return {
                    'domain': {'partner_id': [('id', 'in', vendors.ids)]}
                }

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.partner_id:
            res.sales_rep = res.partner_id.sales_rep
        return res
