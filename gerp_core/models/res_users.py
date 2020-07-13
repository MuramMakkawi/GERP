# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    department_id = fields.Many2one('hr.department','Department', required="True")