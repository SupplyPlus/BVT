from odoo import fields, models,api


# product

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_id = fields.Char(string="Order ID")
    driver_id = fields.Many2one('driver', string="Driver")
    order_status = fields.Selection(
        [
            ("confirmed", "Order confirmed"),
            ("ready_to_dispatch", "Ready to Dispatch"),
            ("on_the_way", "Order on the way"),
            ("delivered", "Order Delivered"),

            ("partially_return_placed", "Partially Return Placed"),
            ("partially_return_picked", "Partially Return Picked"),
            ("partially_return_completed", "Partially Return Completed"),
            ("return_placed", "Return Placed"),
            ("return_picked", "Return Picked"),
            ("return_completed", "Return Completed"),
            ("cancelled", "Cancelled")

        ],
        string="Order Status"
    )