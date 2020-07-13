# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class Employee(models.Model):
    """
    A class contain age field to calculate employee age
    """
    _inherit = 'hr.employee'

    age = fields.Integer(string="Age", compute='_compute_age')

    @api.one
    @api.depends('birthday')
    def _compute_age(self):
        """
        A method to calculate age
        """
        if self.birthday:
            date = fields.date.today()
            self.age = relativedelta(date, self.birthday).years
