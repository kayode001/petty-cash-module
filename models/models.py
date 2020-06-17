# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Kay_petty_cash(models.Model):
    _name="kay.petty.cash"

    name= fields.Char(string="Petty Cash name")
    custodian = fields.Many2one('res.partner',string="Custodian")
    payable_account = fields.Many2one('account.account',string="Account payable")
    custodian_account =  fields.Many2one('account.account',string="Custodian Account")
    date = fields.Date(string="Payment Date")
    amount = fields.Float(string="Amount Allocated")
    amount_left = fields.Float(string="Amount left",compute="_compute_amount_left")
    journal_id= fields.Many2one("account.journal",string="Journal",default=lambda self: self.env['account.journal'].search([('name','=','Petty Cash')]))
    currency_id = fields.Many2one(
        'res.currency', string='Currency',default=lambda self: self.env['res.currency'].search([('name','=','NGN')]))
    state = fields.Selection([
                  	('draft','Draft'),
       			 ('validate','Validated'),
				('closed','Closed')
        		 ],default='draft')
    cash_line = fields.One2many('petty.cash.line','petty_cash_id',string="Cash Lines")


    def _compute_amount_left(self):
	amount_left = 0.0
        for a in self:
            for b in a.cash_line:
                amount_left =amount_left + b.amount
            a.amount_left = a.amount - amount_left

    def action_validate(self):
	print('sdksjkj')
        for rec in self:
            debit = credit = rec.currency_id.compute(rec.amount, rec.currency_id)
            move = {
             'name': '/',
             'journal_id': rec.journal_id.id,
             'date': rec.date,

             'line_ids': [(0, 0, {
                     'name': rec.name or '/',
                     'debit': debit,
                     'account_id': rec.payable_account.id,
                     'partner_id': rec.custodian.id,
                 }), (0, 0, {
                     'name': rec.name or '/',
                     'credit': credit,
                     'account_id': rec.custodian_account.id,
                     'partner_id': rec.custodian.id,
                 })]
            }
            move_id = self.env['account.move'].create(move)
            move_id.post()
            return rec.write({'state': 'validate'})



class kay_petty_cash_line(models.Model):

     _name ="petty.cash.line"    

     description= fields.Text(string="Description")
     amount = fields.Float(string="Amount")
     analytic_account = fields.Many2one('account.analytic.account',string="Analytic Account")
     analytic_tag = fields.Many2one('account.analytic.tag',string="Analytic Tags")
     petty_line_account = fields.Many2one('account.account',string="Account")  
     date = fields.Date(string="Expense Date")
     currency_id = fields.Many2one(
        'res.currency', string='Currency',default=lambda self: self.env['res.currency'].search([('name','=','NGN')]))

     petty_cash_id = fields.Many2one('kay.petty.cash', string='Petty Cash Reference',
        ondelete='cascade', index=True)     
     state = fields.Selection([
                        ('draft','Not Posted'),
                         ('posted','Posted'),
                    
                         ],default='draft')


     def action_post_line(self):
         for rec in self:
             debit = credit = rec.currency_id.compute(rec.amount, rec.currency_id)
             move = {
             'name': '/',
             'journal_id': rec.petty_cash_id.journal_id.id,
             'date': rec.date,

             'line_ids': [(0, 0, {
                     'name': rec.petty_cash_id.name or '/',
                     'debit': debit,
                     'account_id': rec.petty_cash_id.custodian_account.id,
		     'analytic_account_id':rec.analytic_account.id,
                     'partner_id': rec.petty_cash_id.custodian.id,
                 }), (0, 0, {
                     'name': rec.petty_cash_id.name or '/',
                     'credit': credit,
	             'analytic_account_id':rec.analytic_account.id,
                    # 'account_id': rec.petty_cash_id.journal_id.default_credit_account_id.id,
                      'account_id': rec.petty_line_account.id, 
                     'partner_id': rec.petty_cash_id.custodian.id,
                 })]
            }
             move_id = self.env['account.move'].create(move)
             move_id.post()
             return rec.write({'state': 'posted'})
        

#    account_ = fields.May2many('account.journal',domain=['type','in',['bank','cash']])


#   def _compute_journal(self):
#     for a i
