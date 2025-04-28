# -*- coding: utf-8 -*-
# from odoo import http


# class IdsJournalSerial(http.Controller):
#     @http.route('/ids_journal_serial/ids_journal_serial', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ids_journal_serial/ids_journal_serial/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ids_journal_serial.listing', {
#             'root': '/ids_journal_serial/ids_journal_serial',
#             'objects': http.request.env['ids_journal_serial.ids_journal_serial'].search([]),
#         })

#     @http.route('/ids_journal_serial/ids_journal_serial/objects/<model("ids_journal_serial.ids_journal_serial"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ids_journal_serial.object', {
#             'object': obj
#         })
