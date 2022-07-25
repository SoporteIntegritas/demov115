# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
import logging
_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    is_donation = fields.Boolean(string="Is donation", help="Is the payment a donation")

    def _finalize_post_processing(self):
	try:
        	super()._finalize_post_processing()
	except Exception as e:
		_logger.exception(e)
