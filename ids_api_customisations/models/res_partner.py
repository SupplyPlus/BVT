from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_res_partner_api_call(self):
        """Api call wizard from res partner model"""
        record_ids = self._context.get('active_ids')
        if record_ids:
            return {
                'name': "Update To App",
                'type': 'ir.actions.act_window',
                'res_model': 'api.call.wizard',
                'target': 'new',
                'view_id': self.env.ref('ids_api_customisations.api_call_wizard_view').id,
                'view_mode': 'form',
                'context': {
                    'default_vendor_ids': record_ids,
                    'default_is_vendor': True
                }}