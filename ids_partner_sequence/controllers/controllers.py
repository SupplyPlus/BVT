# -*- coding: utf-8 -*-
# from odoo import http


# class IdsPartnerSequence(http.Controller):
#     @http.route('/ids_partner_sequence/ids_partner_sequence', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ids_partner_sequence/ids_partner_sequence/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ids_partner_sequence.listing', {
#             'root': '/ids_partner_sequence/ids_partner_sequence',
#             'objects': http.request.env['ids_partner_sequence.ids_partner_sequence'].search([]),
#         })

#     @http.route('/ids_partner_sequence/ids_partner_sequence/objects/<model("ids_partner_sequence.ids_partner_sequence"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ids_partner_sequence.object', {
#             'object': obj
#         })
