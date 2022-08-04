#-*- coding: utf-8 -*-
from odoo import http
import json
import logging
import pprint

import requests
import werkzeug
from werkzeug import urls

from odoo import http
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.http import request
#from odoo.addons.mx_integritas_payment_baz.models.payment import *
from datetime import datetime



_logger = logging.getLogger(__name__)


class BazController(http.Controller):
    _notify_url = '/payment/baz/ipn/'
    _return_url = '/payment/baz/dpn/'
    _cancel_url = '/payment/baz/cancel/'

    
    #@http.route('/process_baz', type='http', auth='public', methods=['POST'], csrf=False)
    #def baz_process(self, **post):
    @staticmethod
    def baz_param_request():

        tipo_operacion = 'ecommerce3D'
        #amount = str(post.get('amount'))
        #email = post.get('email').lower()
        #item_number = post.get('item_number')
        #item_name = post.get('item_name')
        
        #id_transaccion = datetime.utcnow().strftime('000%Y%m%d%H%M%S%f')[:-3]
        ip_address = request.httprequest.environ['REMOTE_ADDR']
        nav = request.httprequest.environ['HTTP_USER_AGENT']
        url_procedencia = str(request.httprequest.environ['HTTP_REFERER']) + '/baz'
        self_request = http.request.env['payment.acquirer'].sudo()
        data = request.httprequest.environ
        
        return {'ip_address':ip_address,'nav':nav,'url_procedencia':url_procedencia,'data':data}

   