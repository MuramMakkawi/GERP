# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrSalaryRule(models.Model):
    """"""
    _inherit = "hr.salary.rule"

    use_type = fields.Selection(selection_add=[('loan', 'Loan')])
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', company_dependent=True)
