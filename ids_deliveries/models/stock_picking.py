from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('partner_id'):
                partner = self.env['res.partner'].browse(vals.get('partner_id'))
                if partner and partner.responsible_id:
                    vals['user_id'] = partner.responsible_id.id
        return super(StockPicking, self).create(vals_list)



