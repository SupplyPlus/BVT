# -*- coding: utf-8 -*-
# from odoo import http


# class IdsPartnerFilter(http.Controller):
#     @http.route('/ids_partner_filter/ids_partner_filter', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ids_partner_filter/ids_partner_filter/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ids_partner_filter.listing', {
#             'root': '/ids_partner_filter/ids_partner_filter',
#             'objects': http.request.env['ids_partner_filter.ids_partner_filter'].search([]),
#         })

#     @http.route('/ids_partner_filter/ids_partner_filter/objects/<model("ids_partner_filter.ids_partner_filter"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ids_partner_filter.object', {
#             'object': obj
#         })
