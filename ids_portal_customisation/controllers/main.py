from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class PurchasePortal(http.Controller):

    @http.route(['/my/receipt/', '/my/receipt/<int:purchase_order_id>'], type='http', auth="user", website=True)
    def portal_my_purchase_receipt(self, purchase_order_id, **kwargs):
        if purchase_order_id:
            purchase_order = request.env['purchase.order'].sudo().browse(purchase_order_id)

        receipts = request.env['stock.picking'].sudo().search([('purchase_id', '=', purchase_order.id)])

        # Render the template with purchase order and receipt data
        return request.render("ids_portal_customisation.portal_my_purchase_receipt", {
            'purchase_order': purchase_order,
            'receipts': receipts,
            'page_name': 'receipt',
        })



class CustomerPortal(portal.CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        PurchaseOrder = request.env['purchase.order']
        if 'rfq_count' in counters:
            values['rfq_count'] = PurchaseOrder.search_count([
                ('state', 'in', ['sent', 'draft'])
            ]) if PurchaseOrder.check_access_rights('read', raise_exception=False) else 0
        return values

    @http.route(['/my/rfq', '/my/rfq/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_requests_for_quotation(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None,
                                         **kw):
        return self._render_portal(
            "purchase.portal_my_purchase_rfqs",
            page, date_begin, date_end, sortby, filterby,
            [('state', 'in', ['sent', 'draft'])],
            {},
            None,
            "/my/rfq",
            'my_rfqs_history',
            'rfq',
            'rfqs'
        )