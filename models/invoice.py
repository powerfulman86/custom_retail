from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    retail_driver_id = fields.Many2one(comodel_name='retail.driver', string='Driver')
