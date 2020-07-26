# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockLocation(models.Model):
    _inherit = 'stock.location'

    department_id = fields.Many2one('hr.department', 'Department')

    