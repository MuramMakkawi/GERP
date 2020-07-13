# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrSalaryRule(models.Model):
    """"""
    _inherit = 'hr.salary.rule'

    required_partner=fields.Boolean('Need Partner', help=' Total amount in this rule needed to be distributed by partner ')       
    use_type = fields.Selection(string='Use Type',selection=[('general', 'General'), ('special', 'Special')], default='general')

    @api.model
    def compute_rule_amount(self, emp_id):
        """
        A method to compute rule amount
        """

        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
            return localdict


        class BrowsableObject(object):

            def __init__(self, employee_id, dict, env):
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        #TODO: Class to get the working day of an employee from the paslip


        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
                    FROM hr_payslip as hp, hr_payslip_worked_days as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0
        
        #TODO: Class for the payslips


        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
                            FROM hr_payslip as hp, hr_payslip_line as pl
                            WHERE hp.employee_id = %s AND hp.state = 'done'
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
                            (self.employee_id, from_date, to_date, code))
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

        """  MY SOULTIONS """
        #TODO: Get the paysilp of the current employee
        payslip = self.env['hr.payslip'].search([('employee_id','=',emp_id.id)],limit=1)
        #TODO: Get the working Days from the paysliyp
        worked_days_dict = {}
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days_dict[worked_days_line.code] = worked_days_line


        """ END OF MY SOLUTION """
        result_amount = 0.0
        rules_dict = {}
        blacklist = []
        
        contract = self.env['hr.contract'].search([('employee_id','=',emp_id.id),('state','in',['open','offer'])],limit=1)
        if not contract:
            raise ValidationError(_("There is no running contract for this Employee %s.")%(emp_id.name))
        employee = emp_id
        categories = BrowsableObject(emp_id.id, {}, self.env)
        rules = BrowsableObject(emp_id.id, rules_dict, self.env)
        payslips = Payslips(payslip.employee_id.id, payslip, self.env)
        baselocaldict = {'categories': categories, 'rules': rules, 'payslips': payslips}
        localdict = dict(baselocaldict,employee=employee, contract=contract)
        rule_ids=self._recursive_search_of_rules()
        #run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

        for rule in sorted_rules:
            key = rule.code + '-' + str(contract.id)
            localdict['result'] = None
            localdict['result_qty'] = 1.0
            localdict['result_rate'] = 100
            #check if the rule can be applied
            if rule._satisfy_condition(localdict) and rule.id not in blacklist:
                #compute the amount of the rule
                amount, qty, rate = rule._compute_rule(localdict)
                print(amount)
                print(qty)
                print(rate)
                #check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                #set/overwrite the amount computed for this rule in the localdict
                tot_rule = amount * qty * rate / 100.0
                localdict[rule.code] = tot_rule
                # rules_dict[rule.code] = rule
                #sum the amount for its salary category
                localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                #create/overwrite the rule in the temporary results
                result_amount += tot_rule
            else:
                #blacklist this rule and its children
                blacklist += [id for id, seq in rule._recursive_search_of_rules()]
        return result_amount
''' Contract 
[{'id': 127, 'advantages': False, 'notes': False, 'reported_to_secretariat': False, 'active': True, 'employee_id': (85, 'Ameen Tahir Hamd'), 'department_id': False, 'type_id': (1, 'Employee'), 'date_start': datetime.date(2008, 1, 1), 'date_end': False, 'trial_date_end': False, 'hour_wage': 86.875, 'joining_date': datetime.date(2008, 1, 1), 'service_years': 0.0, 'struct_id': (101, 'Carawan Structure'), 'schedule_pay': 'monthly', 'resource_calendar_id': (1, 'Standard 40 Hours/Week'), 'analytic_account_id': False, 'journal_id': False, 'cooperative_fund': 0.0, 'health_insu': 0.0, 'line_ids': [], 'company_id': (1, 'Carawan Holding'), 'age': 0, 'name': 'Contract/2019/0007', 'income_tax_exemption': True, 'custody_ids': [], 'grade_id': False, 'level_id': False, 'wage': 20850.0, 'state': 'open', 'activity_ids': [], 'message_follower_ids': [], 'message_ids': [1598, 1030, 854], 'message_main_attachment_id': False, 'website_message_ids': [], 'job_id': False, 'appraisal_send': False, 'appraisal_pass': False, 'appraisal_fail': False, 'create_uid': (2, 'Administrator'), 'create_date': datetime.datetime(2019, 11, 19, 11, 49, 48, 996835), 'write_uid': (2, 'Administrator'), 'write_date': datetime.datetime(2020, 3, 1, 8, 24, 50, 305035), 'currency_id': (144, 'SDG'), 'permit_no': False, 'visa_no': False, 'visa_expire': False, 'contract_template': False, 'offer_template': False, 'website_description': False, 'offer_website_description': False, 'activity_state': False, 'activity_date_deadline': False, 'message_is_follower': False, 'message_partner_ids': [], 'message_channel_ids': [], 'message_unread': False, 'message_unread_counter': 0, 'message_needaction': False, 'message_needaction_counter': 0, 'message_has_error': False, 'message_has_error_counter': 0, 'message_attachment_count': 0, 'activity_user_id': False, 'activity_type_id': False, 'activity_summary': False, 'display_name': 'Contract/2019/0007', '__last_update': datetime.datetime(2020, 3, 1, 8, 24, 50, 305035)}]
'''