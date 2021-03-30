# -*- coding: utf-8 -*-
# from odoo import http


# class CustomRetail(http.Controller):
#     @http.route('/custom_retail/custom_retail/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_retail/custom_retail/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_retail.listing', {
#             'root': '/custom_retail/custom_retail',
#             'objects': http.request.env['custom_retail.custom_retail'].search([]),
#         })

#     @http.route('/custom_retail/custom_retail/objects/<model("custom_retail.custom_retail"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_retail.object', {
#             'object': obj
#         })
