# -*- coding: utf-8 -*-
# from odoo import http


# class PlAccountingUpdates(http.Controller):
#     @http.route('/ids_accounting_updates/ids_accounting_updates', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ids_accounting_updates/ids_accounting_updates/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ids_accounting_updates.listing', {
#             'root': '/ids_accounting_updates/ids_accounting_updates',
#             'objects': http.request.env['ids_accounting_updates.ids_accounting_updates'].search([]),
#         })

#     @http.route('/ids_accounting_updates/ids_accounting_updates/objects/<model("ids_accounting_updates.ids_accounting_updates"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ids_accounting_updates.object', {
#             'object': obj
#         })
