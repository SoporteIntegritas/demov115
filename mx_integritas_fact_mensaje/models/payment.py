# -*- coding: utf-8 -*-

# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
import logging
_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):

    _inherit = 'payment.transaction'

    def _reconcile_after_done(self):
        try:
            super()._reconcile_after_done()
        except Exception as e:
            for tx in self.filtered(lambda t: t.operation != 'validation' and not t.payment_id):
            tx._create_payment()
