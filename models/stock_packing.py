# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class ProductTemplate(models.Model):
    _inherit = "product.template"

    pack_line_ids = fields.One2many('product.packing', 'product_id', 'Product Packs',
                                    copy=True)


class StockMove(models.Model):
    _inherit = "stock.move"

    pack_id = fields.Many2one('stock.pack', 'Pck Line', index=True)


class ProductPacking(models.Model):
    _name = 'product.packing'
    _description = "Product Packing"
    _order = 'sequence'

    name = fields.Char('Pack Type', compute='_compute_name', required=False, readonly=True)
    sequence = fields.Integer('Sequence', default=1, help="The first in the sequence is the default one.")
    product_id = fields.Many2one('product.product', string='Product', required=True)
    pack_product_id = fields.Many2one('product.product', string='Pack Product', required=True)
    pack_product_uom = fields.Many2one('uom.uom', string='Unit of Measure',
                                       domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='pack_product_id.uom_id.category_id')
    note = fields.Text('Notes')
    active = fields.Boolean(default=True)

    @api.depends('pack_product_id', 'pack_product_uom')
    def _compute_name(self):
        for rec in self:
            rec.name = str(rec.pack_product_id.name) + ' - ' + str(rec.pack_product_uom.name)


class StockPack(models.Model):
    _name = 'stock.pack'
    _description = 'Stock Packing'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _rec_name = 'name'
    _order = 'id desc'

    @api.model
    def _default_warehouse_id(self):
        # !!! Any change to the default value may have to be repercuted
        # on _init_column() below.
        return self.env.user._get_default_warehouse_id()

    name = fields.Char('Reference', default='/', copy=False, index=True, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', copy=False, index=True, tracking=3, default='draft')

    user_id = fields.Many2one(
        'res.users', string='User', index=True, tracking=2, default=lambda self: self.env.user)
    order_date = fields.Date(string='Order Date', copy=False,
                             states={'draft': [('readonly', False)]}, default=fields.Date.context_today)
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True, default=_default_warehouse_id, check_company=True)

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id.id)
    note = fields.Text('Terms and conditions')
    order_line = fields.One2many('stock.pack.line', 'order_id', string='Stock Packing Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                 auto_join=True)
    location_id = fields.Many2one('stock.location', related='warehouse_id.lot_stock_id', store=True)
    move_ids = fields.One2many('stock.move', 'pack_id', string='Stock Moves')

    @api.depends('warehouse_id')
    def _lot_location(self):
        return self.warehouse_id.lot_stock_id

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

    # @api.depends('warehouse_id')
    # @api.onchange('warehouse_id')
    # def set_location_id(self):
    #     if self.warehouse_id:
    #         self.location_id = self.warehouse_id.lot_stock_id

    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel'])
        return orders.write({'state': 'draft', })

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_done(self):
        # insert lines in tender lines
        if len(self.order_line) == 0:
            raise UserError(_('You Must Select Products For Order.'))

        for line in self.order_line:
            line._generate_moves()
        self.mapped('move_ids').filtered(lambda move: move.state != 'done')._action_done()
        return self.write({'state': 'done'})

    def action_approve(self):
        if len(self.order_line) == 0:
            raise UserError(_('You Must Select Products For Order.'))

        return self.write({'state': 'approve'})


class StockPackLine(models.Model):
    _name = 'stock.pack.line'
    _rec_name = 'name'
    _description = 'Stock Packing Line'

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Text(string='Description', )
    order_id = fields.Many2one('stock.pack', string='Stock Pack Order', required=False,
                               ondelete='cascade', index=True, copy=False)

    company_id = fields.Many2one(comodel_name='res.company', related='order_id.company_id', store=True, )
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', related='order_id.warehouse_id', store=True, )
    location_id = fields.Many2one('stock.location', related='order_id.location_id', store=True, )
    order_date = fields.Date(string='Order Date', related='order_id.order_date', store=True, )
    pack_id = fields.Many2one('product.packing', required=True)
    product_id = fields.Many2one('product.product', string='Product', )
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', )
    product_qty = fields.Float('Qty', digits=0, required=True, )
    product_uom_qty = fields.Float('Pack Qty', default=0.0, digits='Product Unit of Measure', required=True)
    pack_product_id = fields.Many2one('product.product', string='Pack Product', )
    pack_product_uom = fields.Many2one('uom.uom', string='Unit of Measure', )

    @api.depends('product_id', 'product_uom_id', 'product_qty')
    @api.onchange('product_qty')
    def _compute_product_qty(self):
        for line in self:
            line.product_uom_qty = line.product_uom_id._compute_quantity(line.product_qty, line.pack_product_uom)

    @api.onchange('pack_id')
    def set_products(self):
        if self.pack_id:
            self.product_id = self.pack_id.product_id
            self.product_uom_id = self.product_id.uom_id
            self.pack_product_id = self.pack_id.pack_product_id
            self.pack_product_uom = self.pack_id.pack_product_uom

    def _get_virtual_location(self):
        return self.product_id.with_company(self.company_id).property_stock_inventory

    def _get_move_values(self, product, qty, location_id, location_dest_id, out):
        self.ensure_one()
        return {
            'name': _('INV:') + (self.order_id.name or ''),
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': qty,
            'date': self.order_id.order_date,
            'company_id': self.order_id.company_id.id,
            'pack_id': self.order_id.id,
            'state': 'confirmed',
            'restrict_partner_id': False,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'move_line_ids': [(0, 0, {
                'product_id': product.id,
                'lot_id': False,
                'product_uom_qty': 0,  # bypass reservation here
                'product_uom_id': product.uom_id.id,
                'qty_done': qty,
                'package_id': False,
                'result_package_id': False,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'owner_id': False,
            })]
        }

    def _generate_moves(self):
        vals_list = []
        for line in self:
            virtual_location = line._get_virtual_location()
            # source product
            original_val = line._get_move_values(line.product_id, abs(line.product_qty), line.location_id.id,
                                                 virtual_location.id, True)
            vals_list.append(original_val)

            # destination product
            dest_val = line._get_move_values(line.pack_product_id, line.product_qty, virtual_location.id,
                                             line.location_id.id, False)
            vals_list.append(dest_val)

            # if line.difference_qty > 0:  # found more than expected
            #     vals = line._get_move_values(line.difference_qty, virtual_location.id, line.location_id.id, False)
            # else:
            #     vals = line._get_move_values(abs(line.difference_qty), line.location_id.id, virtual_location.id, True)
            # vals_list.append(vals)
        return self.env['stock.move'].create(vals_list)
