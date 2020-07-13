# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfig(models.TransientModel):
    _inherit = 'res.config.settings'
    module_voucher_regester_payment = fields.Boolean(string="Voucher Register Payment")
