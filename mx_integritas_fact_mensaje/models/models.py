# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class mx_integritas_fact_mensaje(models.Model):
#     _name = 'mx_integritas_fact_mensaje.mx_integritas_fact_mensaje'
#     _description = 'mx_integritas_fact_mensaje.mx_integritas_fact_mensaje'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
