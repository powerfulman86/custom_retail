# -*- coding: utf-8 -*-

from odoo import models, api, tools


class Menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        menus = super(Menu, self)._visible_menu_ids(debug)
        sale_menu = self.env.ref('sale.sale_menu_root')
        purchase_menu = self.env.ref('purchase.menu_purchase_root')
        inventory_menu = self.env.ref('stock.menu_stock_root')
        calendar_menu = self.env.ref('calendar.mail_menu_calendar')
        account_menu = self.env.ref('account.menu_finance')
        contact_menu = self.env.ref('contacts.res_partner_menu_config')
        board_menu = self.env.ref('board.menu_board_my_dash')

        if sale_menu:
            menus.discard(sale_menu.id)
        if purchase_menu:
            menus.discard(purchase_menu.id)
        if inventory_menu:
            menus.discard(inventory_menu.id)
        if calendar_menu:
            menus.discard(calendar_menu.id)
        if account_menu:
            menus.discard(account_menu.id)
        if contact_menu:
            menus.discard(contact_menu.id)
        # if board_menu:
        #     menus.discard(board_menu.id)
        return menus
