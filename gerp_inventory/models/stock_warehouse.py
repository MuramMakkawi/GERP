# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    department_id = fields.Many2one('hr.department','Department', required="True")

    