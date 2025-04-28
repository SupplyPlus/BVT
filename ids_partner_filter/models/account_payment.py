from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    partner_seq = fields.Char(
        string='Partner Sequence',
        required=False)
    sales_rep = fields.Many2one(
        comodel_name='sales.repo',
        string='Sales Rep',
        required=False, )

    @api.onchange("partner_id")
    def get_sales_rep(self):
        for payment in self:
            payment.sales_rep = payment.partner_id.sales_rep

    @api.onchange("payment_type")
    def get_filter(self):
        for payment in self:
            if payment.payment_type == 'inbound':
                customers = self.env['res.partner'].search([('customer_rank', '>', 0)])
                return {
                    'domain': {'partner_id': [('id', 'in', customers.ids)]}
                }
            if payment.payment_type == 'outbound':
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
