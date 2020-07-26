# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def default_get(self, fields):
        res = super(PurchaseOrderLine, self).default_get(fields)
        user = self.env['res.users'].search([('id', '=', self.env.context['uid'])])
        res['account_analytic_id'] = user.department_id.account_analytic_id.id or False
        return res
