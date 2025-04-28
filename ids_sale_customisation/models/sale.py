from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_cancel(self):
        purchase_orders = self._get_purchase_orders()
        if purchase_orders:
            done_po = purchase_orders.filtered(lambda p: p.state in ('purchase', 'done'))
            if done_po:
                raise ValidationError("Order cannot be cancelled as there are completed purchase orders")
            else:
                for po in purchase_orders:
                    po.button_cancel()
        return super().action_cancel()



