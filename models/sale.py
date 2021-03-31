# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    edit = fields.Boolean(related="order_id.edit")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    edit = fields.Boolean()

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for pick in self.picking_ids:
            for line in pick.move_ids_without_package:
                line.quantity_done = line.product_uom_qty
            pick.button_validate()
        self._create_invoices()
        for inv in self.invoice_ids:
            inv.action_post()
        self.edit = False
        self.action_done()
        return res

    def edit_price(self):
        self.action_unlock()
        self.edit = True

    def update_price(self):
        invoices = []
        for inv in self.invoice_ids:
            invoices.append(inv.id)
            inv.button_draft()
            inv.button_cancel()
        self._create_invoices()
        for inv in self.invoice_ids:
            if inv.id not in invoices:
                inv.button_draft()
                inv.action_post()
        self.action_done()
        # for inv in self.invoice_ids:
        #     for inv_line in inv.invoice_line_ids:
        #         for line in self.order_line:
        #             if line.product_id == inv_line.product_id:
        #                 print("Prodduct ", line.product_id.name)
        #                 inv_line.price_unit = line.price_unit