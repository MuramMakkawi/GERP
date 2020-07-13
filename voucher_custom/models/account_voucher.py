# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountVoucherLine(models.Model):

    _inherit = 'account.voucher.line'
    partner_id = fields.Many2one('res.partner', 'Partner', change_default=1,required=False)


class AccountVoucher(models.Model):

    _inherit = 'account.voucher'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('cancel', 'Cancelled'),
        ('proforma', 'Pro-forma'),
        ('posted', 'Posted'),
        ('paid', 'Paid')
        ], 'Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Voucher.\n"
             " * The 'Pro-forma' status is used when the voucher does not have a voucher number.\n"
             " * The 'Posted' status is used when user create voucher,a voucher number is generated "
             "and voucher entries are created in account.\n"
             " * The 'Cancelled' status is used when user cancel voucher.")

    paid = fields.Boolean(compute='_check_paid', help="The Voucher has been totally paid.")

    @api.one
    @api.depends('move_id.line_ids.reconciled', 'move_id.line_ids.account_id.internal_type','move_id.state')
    def _check_paid(self):
        if self.pay_now == 'pay_now' and self.move_id and self.move_id.state == 'post':
            self.paid = True
        else:
            self.paid = any([((line.account_id.internal_type, 'in', ('receivable', 'payable')) and line.reconciled)
                             for line in self.move_id.line_ids])


    @api.multi
    def first_move_line_get(self, move_id, company_currency, current_currency):
        debit = credit = 0.0
        pay_no_account_id = self.account_id.id
        if self.voucher_type == 'purchase':
            credit = self._convert(self.amount)
            if self.pay_now == "pay_now":
                    pay_no_account_id = self.payment_journal_id.default_debit_account_id.id
        elif self.voucher_type == 'sale':
            debit = self._convert(self.amount)
            pay_no_account_id = self.payment_journal_id.default_credit_account_id.id

        if debit < 0.0: debit = 0.0
        if credit < 0.0: credit = 0.0
        sign = debit - credit < 0 and -1 or 1
        #set the first line of the voucher
        move_line = {
                'name': self.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': self.account_id.id if self.pay_now == "pay_later" else pay_no_account_id ,
                'move_id': move_id,
                'journal_id': self.journal_id.id,
                #'partner_id': self.partner_id.commercial_partner_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': (sign * abs(self.amount)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                'date': self.account_date,
                'date_maturity': self.date_due,
            }
        return move_line

    @api.multi
    def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        tax_calculation_rounding_method = self.env.user.company_id.tax_calculation_rounding_method
        tax_lines_vals = []
        for line in self.line_ids:
            #create one move line per voucher line where amount is not 0.0
            if not line.price_subtotal:
                continue
            line_subtotal = line.price_subtotal
            if self.voucher_type == 'sale':
                line_subtotal = -1 * line.price_subtotal
            # convert the amount set on the voucher line into the currency of the voucher's company
            amount = self._convert(line.price_unit*line.quantity)
            debit = credit = 0.0
            if amount < 0:
                if self.voucher_type == 'sale':
                    debit = abs(amount)
                else:
                    credit = abs(amount)
            if amount > 0:
                if self.voucher_type == 'purchase':
                    debit = abs(amount)
                else:
                    credit = abs(amount)
            move_line = {
                'journal_id': self.journal_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'quantity': line.quantity,
                'product_id': line.product_id.id,
                # 'partner_id': self.partner_id.commercial_partner_id.id,
                'partner_id': self.partner_id.id,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                # 'credit': abs(amount) if self.voucher_type == 'sale' else 0.0,
                # 'debit': abs(amount) if self.voucher_type == 'purchase' else 0.0,
                'credit': credit,
                'debit': debit,
                'date': self.account_date,
                'tax_ids': [(4,t.id) for t in line.tax_ids],
                'amount_currency': line_subtotal if current_currency != company_currency else 0.0,
                'currency_id': company_currency != current_currency and current_currency or False,
                'payment_id': self._context.get('payment_id'),
            }
            # Create one line per tax and fix debit-credit for the move line if there are tax included
            if (line.tax_ids):
                tax_group = line.tax_ids.compute_all(line.price_unit, line.currency_id, line.quantity, line.product_id, self.partner_id)
                if move_line['debit']: move_line['debit'] = tax_group['total_excluded']
                if move_line['credit']: move_line['credit'] = tax_group['total_excluded']
                for tax_vals in tax_group['taxes']:
                    if tax_vals['amount']:
                        tax = self.env['account.tax'].browse([tax_vals['id']])
                        account_id = (amount > 0 and tax_vals['account_id'] or tax_vals['refund_account_id'])
                        if not account_id: account_id = line.account_id.id
                        temp = {
                            'account_id': account_id,
                            'name': line.name + ' ' + tax_vals['name'],
                            'tax_line_id': tax_vals['id'],
                            'move_id': move_id,
                            'date': self.account_date,
                            'partner_id': self.partner_id.id,
                            'debit': self.voucher_type != 'sale' and tax_vals['amount'] or 0.0,
                            'credit': self.voucher_type == 'sale' and tax_vals['amount'] or 0.0,
                            'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                        }
                        if company_currency != current_currency:
                            ctx = {}
                            if self.account_date:
                                ctx['date'] = self.account_date
                            temp['currency_id'] = current_currency.id
                            temp['amount_currency'] = company_currency._convert(tax_vals['amount'], current_currency, line.company_id, self.account_date or fields.Date.today(), round=True)
                        self.env['account.move.line'].create(temp)

            self.env['account.move.line'].create(move_line)
            # When global rounding is activated, we must wait until all tax lines are computed to
            # merge them.
            if tax_calculation_rounding_method == 'round_globally':
                tax_lines_vals += self.env['account.move.line'].with_context(round=False)._apply_taxes(
                    move_line,
                    move_line.get('debit', 0.0) - move_line.get('credit', 0.0)
                )

        # When round globally is set, we merge the tax lines
        if tax_calculation_rounding_method == 'round_globally':
            tax_lines_vals_merged = {}
            for tax_line_vals in tax_lines_vals:
                key = (
                    tax_line_vals['tax_line_id'],
                    tax_line_vals['account_id'],
                    tax_line_vals['analytic_account_id'],
                )
                if key not in tax_lines_vals_merged:
                    tax_lines_vals_merged[key] = tax_line_vals
                else:
                    tax_lines_vals_merged[key]['debit'] += tax_line_vals['debit']
                    tax_lines_vals_merged[key]['credit'] += tax_line_vals['credit']
            currency = self.env['res.currency'].browse(company_currency)
            for vals in tax_lines_vals_merged.values():
                vals['debit'] = currency.round(vals['debit'])
                vals['credit'] = currency.round(vals['credit'])
                self.env['account.move.line'].create(vals)
        return line_total

    @api.multi
    def cancel_voucher(self):
        for voucher in self:
            ## cancel move_id
            #unreconcile all journal items of the invoice, since the cancellation will unlink them anyway
            voucher.move_id.line_ids.filtered(lambda x: x.account_id.reconcile).remove_move_reconcile()
            voucher.move_id.button_cancel()
            voucher.move_id.unlink()

            ## Cancel Payments
            # voucher.payment_ids.cancel()
            # voucher.payment_ids.write({'move_name':''})
            # voucher.payment_ids.unlink()
        self.write({'state': 'cancel', 'move_id': False})
