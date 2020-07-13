from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import except_orm
from odoo.tools.translate import html_translate


class HrLoanPayment(models.Model):
    """"""
    _name = 'loan.payment'
    _inherit = ['mail.thread']
    _description = "Loan Payments as voucher"

    reference = fields.Char('Reference')
    employee_id = fields.Many2one('hr.employee', string="Employee", store=True)
    loan_id = fields.Many2one('hr.loan', string="Loans",
                              domain="[('employee_id', '=', employee_id),('state','=','approve')]")
    loan_line_ids = fields.Many2many('hr.loan.line', string='Installments',
                                     domain="[('loan_id', '=', loan_id),('paid','=',False)]")
    amount = fields.Float('Amount', compute="_get_total_to_paid")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('approve', 'Approved'),
                              ('cancel', 'Cancel')
                              ], string="State", default='draft', track_visibility='onchange', copy=False, )
    voucher_id = fields.Many2one('account.voucher', string='Voucher', track_visibility='onchange')
    date = fields.Date(string="Date", default=date.today())

    @api.one
    def _get_total_to_paid(self):
        """
        A method to get total paid loan amount
        """
        total_to_paid_amount = 0.00
        for loan in self:
            for line in loan.loan_line_ids:
                total_to_paid_amount += line.paid_amount
            self.amount = total_to_paid_amount

    @api.one
    def action_confirmed(self):
        """
        A method to confirm loan payment
        """
        self.write({
            'state': 'confirmed'
        })

    @api.one
    def action_cancel(self):
        """
        A method to cancel loan payment
        """
        self.write({
            'state': 'cancel'
        })

    @api.one
    def action_approve(self):
        """
        A method to approve loan payment
        """
        if not self.loan_id.loan_type.emp_account_id or not self.loan_id.loan_type.treasury_account_id:
            raise except_orm('Warning', "You must enter employee account & Treasury account and journal to approve ")
        if not self.loan_line_ids:
            raise except_orm('Warning', 'You must compute Loan Request before Approved')
        for payment in self:
            journal_id = payment.loan_id.loan_type.journal_id.id
            emp_partner = payment.employee_id.address_home_id.id
            if not emp_partner:
                raise ValidationError(_('Please add Partner for this Employee.'))

            vals = {

                'date': payment.date,
                'partner_id': emp_partner,
                'journal_id': journal_id,
                'voucher_type': 'sale',
                'pay_now': 'pay_now',
                'account_id': payment.loan_id.loan_type.emp_account_id.id,

            }

            voucher_id = self.env['account.voucher'].sudo().create(vals)

            vals = {

                'partner_id': emp_partner,
                'name': payment.reference,
                'account_id': payment.loan_id.loan_type.emp_account_id.id,
                'price_unit': payment.amount,
                'voucher_id': voucher_id.id,
            }

            line = self.env['account.voucher.line'].sudo().create(vals)
            # line.price_subtotal.
            self.write({'state': "approve", 'voucher_id': voucher_id.id})
            payment.loan_line_ids.write({'paid': True})
        return True

    @api.model
    def create(self, values):
        """
        Inherit create method to ensure loan lines was created and then create sequence
        """
        res = super(HrLoanPayment, self).create(values)
        if not res.loan_line_ids:
            raise ValidationError(_('Please add Lines Installments.'))
        loan = res.loan_id.name
        res.reference = loan + self.env['ir.sequence'].get('loan.payment') or ' '

        return res

    @api.multi
    def unlink(self):
        """
        A method to delete loan payment
        """
        for payment in self:
            if payment.state not in ('draft',):
                raise UserError(_('You can not delete record not in draft state.'))
        return super(HrLoanPayment, self).unlink()
