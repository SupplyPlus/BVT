# -*- coding: utf-8 -*-
# from odoo import http


# class IdsAccessRight(http.Controller):
#     @http.route('/ids_access_right/ids_access_right', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ids_access_right/ids_access_right/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ids_access_right.listing', {
#             'root': '/ids_access_right/ids_access_right',
#             'objects': http.request.env['ids_access_right.ids_access_right'].search([]),
#         })

#     @http.route('/ids_access_right/ids_access_right/objects/<model("ids_access_right.ids_access_right"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ids_access_right.object', {
#             'object': obj
#         })
