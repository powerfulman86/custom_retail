from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _purchase_order_domain(self, ids=None):
        """Helper to filter current ids by those that are to invoice."""
        domain = [("invoice_status", "=", "to invoice")]
        if ids:
            domain += [("id", "in", ids)]
        pos = self.env["purchase.order"].search(domain)
        # Use only POs with less qty invoiced than the expected
        pos = pos.filtered(
            lambda order: (
                any(
                    line.qty_invoiced
                    < (
                        line.qty_received
                        if line.product_id.purchase_method == "receive"
                        else line.product_qty
                    )
                )
                for line in order.order_line
            )
        )
        if len(domain) > 1:
            domain[1] = ("id", "in", pos.ids)
        return domain

    def _prepare_batch_invoice_vals(self, partner):
        """Allow to override the invoice defaults by a third module.
        i.e.: set invoice type to in_refund.
        """
        Move = self.env["account.move"].with_context(default_type="in_invoice")
        vals = Move.default_get(Move._fields.keys())
        vals.update({"partner_id": partner.id})
        return vals

    def action_batch_invoice(self):
        """Generate invoices for all selected purchase orders.

        :return dict:
            Window action to see the generated invoices.
        """
        invoices = self.env["account.move"]
        for pogroup in self:
            invoice = invoices.new(
                self._prepare_batch_invoice_vals(pogroup.mapped("partner_id"))
            )
            invoice._onchange_partner_id()
            for po in pogroup:
                invoice.currency_id = po.currency_id
                invoice.purchase_id = po
                invoice._onchange_purchase_auto_complete()
            invoices |= invoices.create(invoice._convert_to_write(invoice._cache))

        action = self.env.ref("account.action_move_in_invoice_type")
        result = action.read()[0]
        result["domain"] = [("id", "in", invoices.ids)]
        return result

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for pick in self.picking_ids:
            for line in pick.move_ids_without_package:
                line.quantity_done = line.product_uom_qty
            pick.button_validate()
        self.action_batch_invoice()
        for inv in self.invoice_ids:
            inv.action_post()
        self.button_done()
        return res

    def edit_price(self):
        self.button_unlock()
        for inv in self.invoice_ids:
            inv.button_draft()
            inv.button_cancel()

    def update_price(self):
        invoices = []
        for inv in self.invoice_ids:
            invoices.append(inv.id)
            inv.button_draft()
            inv.button_cancel()
        self.action_batch_invoice()
        for inv in self.invoice_ids:
            if inv.id not in invoices:
                inv.button_draft()
                inv.action_post()
        self.button_done()

