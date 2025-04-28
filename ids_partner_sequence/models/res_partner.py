from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        ref = res.env['res.partner'].search([('customer_rank', '>', 0)], order='id ASC')
        if ref:
            res['ref'] = int(ref[-2].ref) + 1
        else:
            res['ref'] = 1
        print("@@@@@@@@@@@@@@@@@@@", ref)
        # if res['customer_rank']:
        #     res['ref'] = self.env['ir.sequence'].next_by_code('customer.seq.ref')
        if res['supplier_rank']:
            res['ref'] = self.env['ir.sequence'].next_by_code('vendor.seq.ref')
        return res
