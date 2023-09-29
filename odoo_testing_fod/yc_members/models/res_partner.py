from odoo import models, fields, api, _

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    @api.model
    def default_get_request(self):
        # res = super(ResPartnerInherit, self).default_get(fields_list)
        request = []
        request_id = self.env['member.request'].search([('state','=', 'confirm'),('partner_id','=',self.id)])
        print('request==><><><><>',request_id)
        if  request_id:
            for rec in request_id:
                request.append(rec.id)
            return {'domain': {'request_id': [('id', 'in', request)]}}
        else:
            return {'domain': {'request_id': [('id', 'in', request)]}}
    payment_id = fields.Many2one('payment','Payment')
    request_id = fields.Many2one('member.request','Member Request',domain ="[('state','=', 'confirm')]")
    normal_user = fields.Boolean('Normal User', defaut=False)
    payment_count = fields.Integer(string='Bill Count', compute='_compute_payment_count')
    member_request_count = fields.Integer(string='Member Request Count', compute='_compute_member_request_count')

    @api.onchange('payment_id','request_id')
    def onchange_normal_user(self):
        if self.request_id and self.payment_id:
            self.normal_user = False
        else:
            self.normal_user = True

    def _compute_payment_count(self):
        self.payment_count = self.env['payment'].search_count([('partner_id','=',self.id)])

    def button_payment(self):
        # account_ids = self.env['payment'].search([('partner_id','in',self.id)])
        return {
            'name': _('Payment'),
            'view_mode': 'tree,form',
            'res_model': 'payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('partner_id', '=', self.id)],
        }

    def _compute_member_request_count(self):
        self.member_request_count = self.env['member.request'].search_count([('partner_id','=',self.id)])
    
    def action_view_member_request(self):
        action = self.env.ref('yc_members.member_request_action').read()[0]
        action['domain'] = [('partner_id', '=', self.id)]
        return action
