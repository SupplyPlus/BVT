# -*- coding: utf-8 -*-
# from odoo import http


# class PrAccountBookReport(http.Controller):
#     @http.route('/pr_account_book_report/pr_account_book_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pr_account_book_report/pr_account_book_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pr_account_book_report.listing', {
#             'root': '/pr_account_book_report/pr_account_book_report',
#             'objects': http.request.env['pr_account_book_report.pr_account_book_report'].search([]),
#         })

#     @http.route('/pr_account_book_report/pr_account_book_report/objects/<model("pr_account_book_report.pr_account_book_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pr_account_book_report.object', {
#             'object': obj
#         })
