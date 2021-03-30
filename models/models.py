# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class custom_retail(models.Model):
#     _name = 'custom_retail.custom_retail'
#     _description = 'custom_retail.custom_retail'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
