from odoo import fields, models, api


class ModelName(models.Model):
    _name = 'retail.driver'
    _description = 'Retail Driver'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one('res.partner', track_visibility='always')
    note = fields.Text(string="Note", track_visibility='always')