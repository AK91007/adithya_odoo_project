#-*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import Warning, UserError, AccessError,ValidationError
# import logging
# import re
# _logger = logging.getLogger(__name__)

class GateEntry(models.Model):
    """
       One of Main class for this module, contains purchase_order_ids, sale_order_ids [ split into two  inward/outward because conditions for domain
       is different for inward and outward ].And order type is changed based on the entry_type. [ Ex: If entry_type is "in" then it should show ( purchase, sale return)
       if its "out" it should show(sale, purchase return)]. 
       
    """
    _name = 'gate.entry'
    _inherit = ['mail.thread', 'mail.activity.mixin'] #This is inherited to give the chatter box and activity panel
    _description = 'gate entry'
    _order = ' id desc, name desc' #This makes the gate entry tree view to display record in descending order

    name = fields.Char(string='Name')
    entry_type = fields.Selection(string='Entry Type', selection=[('in', 'Inward'),('out','Outward')])
    
    order_type_inward = fields.Selection(string=" Order type", selection=[ ('p','Purchase'), ('sr','Sales Return'),('others','Others')]) # p = purchase, sr = sales return, tin = transefer In
    order_type_outward = fields.Selection(string= "Order type",selection =[ ('s','Sale'), ('pr','Purchase Return'),('others','Others')]) # s = sales, pr = purchase return, t = transefer Out

    username = fields.Many2one("gate.user.registration")
    description = fields.Char()
    # item_description = fields.Char()
    doc_datetime = fields.Datetime("Document Date",help="The datetime entered for user reference",copy=False)
    post_datetime = fields.Datetime("Posting Date",help="The datetime at which the documents get posted",copy=False,default=None)
    lr_rr_no = fields.Char(string="LR/RR/AWL/BL",help="LR - Lorry Receipt \n RR - Railways Receipt \n AWL - Airway Bill \n BL - Bill of Lading")          
        
    lr_rr_date = fields.Datetime(string="LR/RR/AWL/BL Date",help="This is the date in LR/RR/AWL/BL copy",default=None,copy=False)
    # vehicle_no = fields.Many2one('fleet.vehicle',string="Internal Vechile No.")
    external_vehicle_no = fields.Char(string="Vechile No",help="This is the vehicle number")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse",domain=[('activate_gate_entry','=',True)],help="Warehouse where the entry happens")
    
    gate_line = fields.One2many('gate.entry.line', 'gate_id') #This is the data entry field for identifyin transactions
    # station_from = fields.Char()
    # station_to = fields.Char()
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processed', 'Processed'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft')

    #This method raises a user error if vehicle number is not entered
    @api.constrains('warehouse_id') #The warehouse is a required field for all records in gate entry
    def vehicle_number(self):
        if not self.external_vehicle_no:
            raise UserError(_('Please Capture Vehicle Number.'))

    #This method raises a user error if the user tries to do data entry in a non-authorised warehouse
    @api.constrains('warehouse_id')
    def warehouse_name(self):
        if self.username:
            warehouse = self.warehouse_id
            if self.warehouse_id.id != self.username.warehouse_id.id:
                raise UserError(_('You are not authorised to do transaction in %s warehouse.') % ', '.join(warehouse.mapped('name'))) #join and mapped command joins the value in warehouse variable with the name of warehouse
    #This method raises a user error if the user tries to delete an entry which is in processed state
    def unlink(self): #This method restricts the user from deleting the record which has been processed
        for each_entry in self:
            if each_entry.state != 'draft':
                raise UserError(_('You cannot delete an entry which has been Processed once.'))
        return super(GateEntry, self).unlink() #This line signifies that the unlink method in GateEntry class will be called whenever a record is being deleted
    
    #This method is used to create sequence to the gate entry records
    @api.model #api.model decorator is used when the contents of self are not relevant. No ids will be passed with these methods
    def create(self, vals):
        if (self.env.context['default_entry_type'] == 'in'):
            sequence_type =  vals.get('warehouse_id')
            sequence_type = self.env['stock.warehouse'].browse(sequence_type)
            if not sequence_type:
                raise Warning('Inward sequence is not set')
            else: 
                vals['name'] = sequence_type.inward_sequence.next_by_id() #next_by_id method is used to fetch the next number of the sequence in this context
                vals['post_datetime'] = fields.Datetime.now()
        else:
            sequence_type =  vals.get('warehouse_id')
            sequence_type = self.env['stock.warehouse'].browse(sequence_type)
            if not sequence_type:
                raise Warning('Outward sequence is not set')
            else:
                vals['name'] = sequence_type.outward_sequence.next_by_id()
                vals['post_datetime'] = fields.Datetime.now()

        return super(GateEntry, self).create(vals) #This returns the sequence and posting datetime to the respective gate entry document in concern


    def process(self): #This block gets executed when process button is pressed
        for each in self.gate_line:
            if self.entry_type == 'in':
                if each.order_type_inward == 'p':
                    for l in each.purchase_order_inward_ids:
                        for picking in l.picking_ids.filtered(lambda e: e.picking_type_id.code == 'incoming'):
                            if picking.state != 'done':
                                picking.write({'gate_entry_id':self.id})

                if each.order_type_inward == 'sr':
                        for picking in each.sale_return_receipt_ids:
                            if picking.state != 'done':
                                picking.write({'gate_entry_id':self.id})

                if each.order_type_inward == 'others':
                    for l in each.other_inward:
                        for picking in l.filtered(lambda e: e.picking_type_id.code == 'incoming' or e.picking_type_id.code == 'internal' and e.location_id.usage == "inventory"):
                            if picking.state != 'done':
                                picking.write({'gate_entry_id':self.id})

            elif self.entry_type == 'out':
                if each.order_type_outward == 'others':
                    for l in each.other_outward:
                        for picking in l.filtered(lambda e: e.picking_type_id.code == 'outgoing' or e.picking_type_id.code == 'internal' and e.location_dest_id.usage == "inventory"):
                            if picking.state == 'done':
                                if not picking.gate_entry_id:
                                    picking.write({'gate_entry_id':self.id})

                if each.order_type_outward == 's':
                    for picking in each.purchase_return_receipt_ids:
                        if picking.state == 'done':
                            if not picking.gate_entry_id:
                                picking.write({'gate_entry_id':self.id})

                if each.order_type_outward == 'pr':
                    for picking in each.purchase_return_receipt_ids:
                        if picking.state == 'done':
                            picking.write({'gate_entry_id':self.id})
                        # else:
                        #     if picking.id in each.purchase_return_receipt_ids.ids:
                        #         picking.write({'gate_entry_id':self.id})

                # if each.order_type_outward == 'pr':
                #     for picking in each.purchase_return_receipt_ids:
                #         if picking.state == 'done':
                #             picking.write({'gate_entry_purchase_outward_id':self.id})
        return self.write({'state': 'processed'})
    
    def cancle(self):
        return self.write({'state': 'cancel'})

class GateEntryLine(models.Model):
    _name = 'gate.entry.line'
    _description = 'Gate Entry Line'

    challan_no = fields.Char()
    challan_date = fields.Datetime()
    description = fields.Char(string='Item Description')
    
    gate_id = fields.Many2one('gate.entry', string='Gate Id') #This is the gate entry id which will be referenced by the entry line
    sequence = fields.Integer(default=10)
    
    # order_type_inward = fields.Selection(string="Order type", selection=[('p','Purchase'),('sr','Sales Return'),('scin','Sub-Contract'),('tout','Transfer')], domain="[('parent.entry_type', '=', 'out')]")
    # order_type_outward = fields.Selection(string= "Order type",selection =[('s','Sale'),('pr','Purchase Return'),('scout','Sub-Contract'),('tout','Transfer')], domain = "[('parent.entry_type', '=', 'in')]")

    entry_type = fields.Selection(related='gate_id.entry_type', store=True, readonly=False)

    order_type_inward = fields.Selection(related='gate_id.order_type_inward', store=True, readonly=False,string='Order Type')
    order_type_outward = fields.Selection(related='gate_id.order_type_outward', store=True, readonly=False,string=' Order Type')
    

    # warehouse_ids = fields.Many2one("stock.warehouse", string="Warehouse",domain=[('activate_gate_entry','=',True)],compute='compute_warehouse')

    purchase_order_inward_ids = fields.Many2one("purchase.order", string="Purchase Order")
    purchase_order_outward_ids = fields.Many2many("purchase.order", relation="purchase_order_outward_ids_rel", column1="gate_entry_id", column2="purchase_order_id", string=" Purchase Order")
    
    sale_order_inward_ids = fields.Many2many("sale.order", relation="sale_order_inward_ids_rel", column1="gate_entry_id", column2="sale_order_id", string="Sale Order")
    sale_order_outward_ids = fields.Many2many("sale.order", relation="sale_order_outward_ids_rel", column1="gate_entry_id", column2="sale_order_id", string=" Sale Order")
    
    # purchase_receipt_ids = fields.Many2many("stock.picking", realtion="purchase_receipt_ids_rel", column1="gate_entry_id", column2="stock_picking_id" , string= "Receipts")
    other_inward = fields.Many2one('stock.picking',string=' Others',store=True)
    other_outward = fields.Many2one('stock.picking',string='Others',store=True)
    purchase_return_receipt_ids = fields.Many2one("stock.picking", string=" Transfers")
    
    # sale_receipt_ids = fields.Many2many("stock.picking", relation="sale_receipt_ids_rel", column1="gate_entry_id", column2="stock_picking_id" , string= "Receipts")
    sale_return_receipt_ids = fields.Many2one("stock.picking", string= "Transfers")

    def unlink(self):
        for each_entry in self:
            if each_entry.gate_id.state != 'draft':
                raise UserError(_('You cannot delete an entry which has been Processed once.'))
        return super(GateEntryLine, self).unlink()

    @api.onchange('order_type_outward')
    def get_outward_filter(self):
        if self.order_type_outward == 'pr':
            return {'domain': {'purchase_return_receipt_ids':[('purchase_return','=',True),('picking_type_code','=','outgoing')]}}
        elif self.order_type_outward == 's':
            return {'domain': {'purchase_return_receipt_ids':[('purchase_return','!=',True),('picking_type_code','=','outgoing'),('gate_entry_id','=',False),('state','=','done'),('sale_id','!=',False)]}}

    @api.onchange('order_type_inward')
    def get_inward_filter(self):
        if self.order_type_inward == 'sr':
            return {'domain': {'sale_return_receipt_ids':[('purchase_return','=',True),('picking_type_code','=','incoming'),('gate_entry_id','=',False)]}}
        
    # @api.depends('gate_id.warehouse_id')
    # def compute_warehouse(self):
    #     for l in self:
    #         for line in l.gate_id:
    #             l.warehouse_ids = line.warehouse_id.id
class GateEntryName(models.Model):
    #This class is defined to give an option to the user whether gate entry is required or not for a warehouse
    
    _inherit = 'stock.warehouse'
    
    activate_gate_entry = fields.Boolean()
    inward_sequence = fields.Many2one("ir.sequence", string="Inward Sequence")
    outward_sequence = fields.Many2one("ir.sequence", string="Outward Sequence")

    @api.constrains('activate_gate_entry')
    def warehouse_number(self):
        if self.activate_gate_entry:
            if not self.inward_sequence or not self.outward_sequence:
                raise UserError(_('Please Select Both Inward And Outward Sequence.'))


    
class PurchaseOrderDone(models.Model):
    _inherit= "purchase.order"

    warehouse_id = fields.Many2one("stock.warehouse", related="picking_type_id.warehouse_id")
  

class StockPicking(models.Model):
    _inherit="stock.picking"

    gate_entry_id = fields.Many2one('gate.entry',copy=False)
    # gate_entry_purchase_outward_id = fields.Many2one('gate.entry',copy=False)
    purchase_return = fields.Boolean(store=True,compute='compute_purchase_return')
    purchase_boolean = fields.Boolean(string='Purchase Boolean',store=True,compute='compute_purchase_boolean')

    #This method is used to check if a move is a purchase return or not
    @api.depends('move_ids_without_package.origin_returned_move_id')
    def compute_purchase_return(self):
        for l in self:
            for line in l.move_ids_without_package:
                if line.origin_returned_move_id:
                    l.purchase_return = True
                else:
                    l.purchase_return = False

    #This method is used to check if a move is a purchase or not
    @api.depends('purchase_id')
    def compute_purchase_boolean(self):
        for l in self:
            if l.purchase_id:
                l.purchase_boolean = True
            else:
                l.purchase_boolean = False
    #This method raises a validation error when an incoming transfer is tried to validate without doing gate entry
    def button_validate(self):
        res = super(StockPicking,self).button_validate()
        if self.picking_type_id.code != 'outgoing': 
            if self.picking_type_id.code != 'internal':
                if self.picking_type_id.code != 'mrp_operation':
                    if self.picking_type_id.code != 'mrp_operation' and not self.gate_entry_id and self.picking_type_id.warehouse_id.activate_gate_entry:
                        raise ValidationError('Gate Entry Not Done')

        return res

