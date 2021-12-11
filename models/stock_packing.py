# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang


class ProductPacking(models.Model):
    _name = 'product.packing'
    _description = "Product Packing"
    _order = 'sequence'

    name = fields.Char('Package Type', required=False)
    sequence = fields.Integer('Sequence', default=1, help="The first in the sequence is the default one.")
    product_id = fields.Many2one('product.product', string='Product', )
    pack_product_id = fields.Many2one('product.product', string='Pack Product', )
    qty = fields.Float('Contained Quantity', help="Quantity of products contained in the packaging.")
    product_uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', index=True)
    note = fields.Text('Notes')


class StockPack(models.Model):
    _name = 'stock.pack'
    _description = 'Stock Packing'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                       states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    user_id = fields.Many2one(
        'res.users', string='Purchase Person', index=True, tracking=2, default=lambda self: self.env.user)
    order_date = fields.Date(string='Order Date', readonly=True, copy=False,
                             states={'draft': [('readonly', False)]}, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id.id)
    note = fields.Text('Terms and conditions')
    order_line = fields.One2many('stock.pack.line', 'order_id', string='Stock Packing Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                 auto_join=True)

    def unlink(self):
        for order in self:
            if order.state not in ('draft', 'cancel'):
                raise UserError(_('You can not delete a packing Order Which Is Not In Draft State.'))
        return super(StockPack, self).unlink()

    @api.model
    def create(self, values):
        if values.get('name', _('New')) == _('New'):
            seq_date = None
            if 'order_date' in values:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(values['order_date']))
            if 'company_id' in values:
                values['name'] = self.env['ir.sequence'].with_context(force_company=values['company_id']).next_by_code(
                    'stock.pack', sequence_date=seq_date) or _('New')
            else:
                values['name'] = self.env['ir.sequence'].next_by_code('stock.pack',
                                                                      sequence_date=seq_date) or _('New')

        result = super(StockPack, self).create(values)
        return result

    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel'])
        return orders.write({'state': 'draft', })

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_done(self):
        # insert lines in tender lines
        if len(self.request_line) == 0:
            raise UserError(_('You Must Select Products For Order.'))

        return self.write({'state': 'done'})

    def action_approve(self):
        if len(self.request_line) == 0:
            raise UserError(_('You Must Select Products For Order.'))

        return self.write({'state': 'approve'})


class StockPackLine(models.Model):
    _name = 'stock.pack.line'
    _rec_name = 'name'
    _description = 'Stock Packing Line'

    name = fields.Text(string='Description', )
    order_id = fields.Many2one('stock.pack', string='Stock Pack Order', required=False,
                               ondelete='cascade', index=True, copy=False)
    sequence = fields.Integer(string='Sequence', default=10)

    company_id = fields.Many2one(comodel_name='res.company', related='order_id.company_id', required=True, )
