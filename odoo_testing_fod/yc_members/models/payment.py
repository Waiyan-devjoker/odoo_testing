# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from  datetime import datetime, date
from odoo.exceptions import UserError,ValidationError

class Payment(models.Model):
    _name = 'payment'
    # _inherit = ['mail.thread']
    _description = 'Payment'

    name = fields.Char('Name')
    partner_id = fields.Many2one('res.partner','Client')
    request_id = fields.Many2one('member.request', 'Member Request')
    bank_id = fields.Many2one('bank.information', 'Bank Info')
    payment_type =  fields.Selection('Payment Type',related='bank_id.payment_type')
    account_number = fields.Char('Bank Account Number', related='bank_id.account_number')
    account_holder = fields.Char('Bank Account Holder', related='bank_id.account_holder')
    phone = fields.Char('Phone',related='bank_id.phone')
    amount = fields.Float('Amount', related="request_id.price")
    photo = fields.Binary('Photo',attachment=True,max_width=13, max_height=13)
    bank_name = fields.Char('Bank Name')
    client_account_number = fields.Char('Bank Account Number')
    client_account_holder = fields.Char('Bank Account Holder')
    phone = fields.Char('Phone',related='bank_id.phone')
    client_phone = fields.Char('Phone')
    date = fields.Date('Date')
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('paid','Paid')],string="State",default='draft')

    @api.onchange('request_id')
    def onchange_request(self):
        self.partner_id = self.request_id.partner_id

    def action_confirm(self):
        return self.write({'state': 'confirm'})
    
    def action_paid(self):
        self.write({'state': 'paid'})
        self.request_id.action_confirm()
        return self.partner_id.write({'payment_id': self.id,'normal_user':False,'client_type':'gym_member'})
    
    def action_reset(self):
        return self.write({'state': 'draft'})

class BankInformation(models.Model):
    _name = 'bank.information'
    # _inherit = ['mail.thread']
    _description = 'Bank Information'

    name = fields.Char('Name')
    payment_type =  fields.Selection([('bank','Bank Account'),('ewallet','E-wallets')],string="Payment Type", required=True)
    account_number = fields.Char('Bank Account Number')
    account_holder = fields.Char('Bank Account Holder')
    phone = fields.Char('Phone')
    image = fields.Binary('Photo',attachment=True,max_width=13, max_height=13)