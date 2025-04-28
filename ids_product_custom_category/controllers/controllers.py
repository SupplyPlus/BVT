# -*- coding: utf-8 -*-
# from odoo import http


# class IdsProductCustomCategory(http.Controller):
#     @http.route('/ids_product_custom_category/ids_product_custom_category', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ids_product_custom_category/ids_product_custom_category/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ids_product_custom_category.listing', {
#             'root': '/ids_product_custom_category/ids_product_custom_category',
#             'objects': http.request.env['ids_product_custom_category.ids_product_custom_category'].search([]),
#         })

#     @http.route('/ids_product_custom_category/ids_product_custom_category/objects/<model("ids_product_custom_category.ids_product_custom_category"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ids_product_custom_category.object', {
#             'object': obj
#         })
