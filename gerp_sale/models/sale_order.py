# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        user = self.env['res.users'].search([('id', '=', self.env.context['uid'])])
        print('\n\n\n\n\n\n\n\n')
        print(user)
        print('\n\n\n\n\n\n\n\n')
        res['analytic_account_id'] = 1
        return res