# -*- coding: utf-8 -*-
# from odoo import http


# class IdsCustomerType(http.Controller):
#     @http.route('/ids_customer_type/ids_customer_type', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ids_customer_type/ids_customer_type/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ids_customer_type.listing', {
#             'root': '/ids_customer_type/ids_customer_type',
#             'objects': http.request.env['ids_customer_type.ids_customer_type'].search([]),
#         })

#     @http.route('/ids_customer_type/ids_customer_type/objects/<model("ids_customer_type.ids_customer_type"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ids_customer_type.object', {
#             'object': obj
#         })
