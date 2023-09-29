# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from  datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError,ValidationError

class MemberPlan(models.Model):
    _name = 'member.plan'
    # _inherit = ['mail.thread']
    _description = 'Member Plan'
    _rec_name = "member_type"

    appendix = fields.Integer('Appendix')
    member_type =  fields.Char('Member Type')
    member_type_level_id = fields.Many2one('member.type.level', 'Member Type Level')
    duration = fields.Integer('Duration')
    price = fields.Float('Price')
    pros = fields.Text('Pros')
    cons = fields.Text('Cons')

class MemberTypeLevel(models.Model):
    _name = 'member.type.level'
    # _inherit = ['mail.thread']
    _description = 'Member Type Level'

    name = fields.Char('Shop Level')
    appendix = fields.Integer('Appendix')
    duration = fields.Integer('Duration')
    price = fields.Float('Price')
    pros = fields.Text('Pros')
    cons = fields.Text('Cons')
    count = fields.Integer('Count')


class MemberRequest(models.Model):
    _name = 'member.request'
    # _inherit = ['mail.thread']
    _description = 'Member Request'

    name = fields.Char('Name')
    partner_id = fields.Many2one('res.partner',"Client")
    request_type =  fields.Selection([('plan','Plan'),('shop','Shop')],string='Member Type',default='plan')
    member_type_level_id = fields.Many2one('member.type.level', 'Member Type Level')
    member_plan_id = fields.Many2one('member.plan','Member Plan')
    duration = fields.Integer('Duration')
    price = fields.Float('Price')
    pros = fields.Text('Pros')
    cons = fields.Text('Cons')
    date = fields.Date('Date')
    confirm_date = fields.Date('Confirmation Date')
    expired_date = fields.Date('Expired Date')
    state = fields.Selection([('draft','Draft'),('request','Request'),('confirm','Confirm'),('expired','Expired')],string="State",default='draft')
    payment_count = fields.Integer('Payment Count', compute='_compute_payment_count')
    shop_name = fields.Char('Shop Name')

    def name_get(self):
        result = []
        for rec in self:
            if rec.member_type_level_id:
                    member_type = "-"+rec.member_type_level_id.name
            else:
                member_type = ''

            if rec.partner_id:
                partner = "(" + rec.partner_id.name+")"
            else:
                partner = ''
            if rec.member_plan_id:
                plan = "-"+rec.member_plan_id.member_type
            else:
                plan = ''
            if rec.request_type == 'shop':
                request = 'Shop'
                
                result.append((rec.id, '%s%s %s' % (request, member_type, partner)))
            else:
                request = 'Plan'
                result.append((rec.id, '%s%s %s' % (request, plan, partner)))
        return result
    
    @api.onchange('request_type')
    def onchange_request_type(self):
        if self.request_type == 'shop':
            self.member_plan_id = False
        else:
            self.member_type_level_id = False
            self.shop_name = False


    @api.onchange('confirm_date')
    def onchange_expired(self):
        if self.duration:
            self.expired_date = self.confirm_date + relativedelta(months=self.duration)
    def action_request(self):
        return self.write({'state': 'request'})

    def action_confirm(self):
        if self.payment_count == 0:
            raise ValidationError(_('Does not have any payment'))
        if not self.env['payment'].search([('request_id','=',self.id),('state','=','paid')],order='id desc',limit=1):
            raise ValidationError(_('Does not have any paid payment'))

        now = fields.Datetime.now()
        expired_date = False
        if self.duration:
            expired_date = now + relativedelta(months=self.duration)
        self.write({'state': 'confirm','confirm_date': now,'expired_date':expired_date})
        return self.partner_id.write({'request_id': self.id})
    
    def action_expired(self):
        self.partner_id.write({'request_id': None,'payment_id': None,'normal_user':True,'client_type':'user'})
        return self.write({'state': 'expired'})
    
    
    def action_reset(self):
        return self.write({'state': 'draft'})

    
    @api.onchange('member_type_level_id','member_plan_id')
    def onchange_member_request(self):
        if self.member_type_level_id:
            self.price = self.member_type_level_id.price
            self.pros = self.member_type_level_id.pros
            self.cons = self.member_type_level_id.cons
            self.duration = self.member_type_level_id.duration
        if self.member_plan_id:
            self.price = self.member_plan_id.price
            self.pros = self.member_plan_id.pros
            self.cons = self.member_plan_id.cons
            self.duration = self.member_plan_id.duration

    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = self.env['payment'].search_count([('request_id','=',rec.id)])
    
    def action_view_payment(self):
        action = self.env.ref('yc_members.payment_action').read()[0]
        action['domain'] = [('request_id', '=', self.id)]
        return action