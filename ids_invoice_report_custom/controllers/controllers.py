# -*- coding: utf-8 -*-
# from odoo import http


# class IdsInvoiceReportCustom(http.Controller):
#     @http.route('/ids_invoice_report_custom/ids_invoice_report_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ids_invoice_report_custom/ids_invoice_report_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ids_invoice_report_custom.listing', {
#             'root': '/ids_invoice_report_custom/ids_invoice_report_custom',
#             'objects': http.request.env['ids_invoice_report_custom.ids_invoice_report_custom'].search([]),
#         })

#     @http.route('/ids_invoice_report_custom/ids_invoice_report_custom/objects/<model("ids_invoice_report_custom.ids_invoice_report_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ids_invoice_report_custom.object', {
#             'object': obj
#         })
