# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import pdb
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from datetime import datetime, timedelta,date

class ClosePO(models.Model):
    _inherit = 'purchase.order'

  
    open_close_po = fields.Selection([
        ('open_po', 'Open PO'),
        ('close_po', 'Close PO')],string="PO Status",store=True,default='open_po')
    po_entry_done = fields.Boolean(compute="check_po_close_check",store=True, copy=False)

    def close_po(self):
        for line in self.order_line:
            if line.po_done == False:
                line.write({'po_done':True})

    @api.depends('order_line.po_done')
    def check_po_close_check(self):
        for rec in self:
            if rec.order_line:
                if any(rec.order_line.filtered(lambda e:e.po_done == False)):
                    rec.po_entry_done = False
                    rec.open_close_po = 'open_po'
                else:
                    rec.po_entry_done = True
                    rec.open_close_po = 'close_po'
            else:
                rec.po_entry_done = None

class ClosePoLine(models.Model):
    _inherit = 'purchase.order.line'

    po_done = fields.Boolean('PO Done',store=True,compute='get_open_close',inverse='get_inverse_po')

    @api.depends('qty_received')
    def get_open_close(self):
        for line in self:
            if line.qty_received:
                if line.qty_received >= line.product_uom_qty:
                    line.update({'po_done':True,})
                else:
                    line.update({'po_done':False,})
            else:
                line.update({'po_done':False,})

    def get_inverse_po(self):
        pass