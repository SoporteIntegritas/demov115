# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class /odoo/custom/addons/mx_integritas_payment_baz(models.Model):
#     _name = '/odoo/custom/addons/mx_integritas_payment_baz./odoo/custom/addons/mx_integritas_payment_baz'
#     _description = '/odoo/custom/addons/mx_integritas_payment_baz./odoo/custom/addons/mx_integritas_payment_baz'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
