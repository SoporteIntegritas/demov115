# coding: utf-8

import logging
import requests
import pprint
import base64
import hashlib

from requests.exceptions import HTTPError
from werkzeug import urls
from collections import namedtuple

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round

from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment import utils as payment_utils

from Crypto import Random
from Crypto.Cipher import AES
from datetime import datetime
from odoo.addons.mx_integritas_payment_baz.controllers.main import BazController

_logger = logging.getLogger(__name__)
class PaymentAcquirerBaz(models.Model):
	_inherit = 'payment.acquirer'
	provider = fields.Selection(selection_add=[('baz', 'Baz')],ondelete={'baz': 'set default'})
	baz_afiliacion = fields.Char('Afiliacion',  groups='base.group_user')#, required_if_provider='baz'
	baz_id_terminal = fields.Char('Id terminal',  groups='base.group_user')#, required_if_provider='baz'
	block_size = 16

 
	pad = lambda self, s: s + (self.block_size - len(s) % self.block_size) * chr(self.block_size - len(s) % self.block_size)
	unpad = lambda self, s: s[0:-ord(s[-1:])]
	iv = "cDRyNG0zN3IwMVY1cHJvZA=="

	secret_key = "QkFOQ09BWlRFQ0ExMjM0NTY3ODkwMTIzNDU2NzhQUjA="
	
	plain_text = "<bancoazteca><tipoOperacion>ecommerce3D</tipoOperacion><correoComprador>edgar.molina@integritas.mx</correoComprador><idSesion>11111111</idSesion><idTransaccion>1000000000001</idTransaccion><afiliacion>7952739</afiliacion><monto>000000000007000</monto><ipComprador>187.140.144.31</ipComprador><navegador>Mozilla/5.0(Windows_NT_10.0;_Win64;_x64;_rv:76.0)_Gecko/20100101_Firefox/76.0</navegador><sku>IMPPREDIAL</sku><url>http://187.217.66.205:99/api/infraccion</url></bancoazteca>"
	plain_text = "<bancoAzteca><eservices><request><canalEntrada>ecommerce</canalEntrada><idterminal>9562</idterminal><tipo_operacion>200</tipo_operacion><idTransaccion>APVV-7043220-2001760800767</idTransaccion></request></eservices></bancoAzteca>"

	def _get_default_payment_method_id(self):
		self.ensure_one()
		if self.provider != 'baz':
			return super()._get_default_payment_method_id()
		return self.env.ref('mx_integritas_payment_baz.payment_method_baz').id

	def getSession(self,item_number):
		
		headers = {'Content-Type': 'application/xml'}
		canalEntrada = 'ecommerce'
		id_terminal =   str(self.search(['|',('provider', '=', 'baz'),('provider', '=', 'Baz')]).baz_id_terminal)
		print(id_terminal)
		tipo_operacion = '200'
		#id_transaccion =  datetime.utcnow().strftime('BAZ-%Y%m%d%M%S%f')[:-2]
		id_transaccion = item_number
		if id_terminal and id_terminal and tipo_operacion and id_transaccion:
			xml='''<?xml version='1.0' encoding='utf-8'?>
			<soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://service.btb.com">
			    <soapenv:Header/>
			        <soapenv:Body>
			            <ser:getToken soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
			            <xml xsi:type="xsd:string">
			                <![CDATA[
			                <bancoAzteca><eservices><request><canalEntrada>'''+canalEntrada+'''</canalEntrada><idterminal>'''+id_terminal+'''</idterminal><tipo_operacion>'''+tipo_operacion+'''</tipo_operacion><idTransaccion>'''+id_transaccion+'''</idTransaccion></request></eservices></bancoAzteca>
			                ]]>
			            </xml>
			        </ser:getToken>
			    </soapenv:Body>
			</soapenv:Envelope>'''
			headers = {'SOAPAction': 'add', 'Content-Type': 'text/xml; charset=utf-8'}
			r =requests.post('http://www.puntoazteca.com.mx/BusinessToBusinessWS/services/PB2B?wsdl',headers=headers,data=xml)
			xml=r.text
			_logger.info(xml)
			xml=xml.replace('<?xml version="1.0" encoding="utf-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><soapenv:Body><ns1:getTokenResponse soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:ns1="http://service.btb.com"><getTokenReturn xsi:type="xsd:string">&lt;bancoazteca&gt;&lt;eservices&gt;&lt;response&gt;&lt;data_service&gt;&lt;token&gt;','')
			token=xml.replace('&lt;/token&gt;&lt;/data_service&gt;&lt;/response&gt;&lt;/eservices&gt;&lt;/bancoazteca&gt;</getTokenReturn></ns1:getTokenResponse></soapenv:Body></soapenv:Envelope>','')
			#llave=xml
			_logger.info("-----Token--")
			_logger.info(token)
			_logger.info("---")
			return token, id_transaccion
		else:
			return None, None

	def getUrl(self, typeLink):
		if typeLink == 'session':
			url = "https://www.puntoazteca.com.mx/BusinessPAYWeb/RealizaVenta?doc="
		elif typeLink == 'request':
			url = "https://www.puntoazteca.com.mx/BusinessPAYWeb/RealizaVenta?doc="
		return url
	def _baz_get_get_api_url(self):
		print("_baz_get_get_api_url")
		self.ensure_one()
		environment = 'prod' if self.state == 'enabled' else 'test'
		url = self.getUrl('request')
		params = "<bancoazteca><tipoOperacion>ecommerce3D</tipoOperacion><correoComprador>correcomprador@gmail.com</correoComprador><idSesion>11111111</idSesion><idTransaccion>1000000000001</idTransaccion><afiliacion>"+self.baz_afiliacion+"</afiliacion><monto>000000000000010</monto><ipComprador>187.140.144.31</ipComprador><navegador>Mozilla/5.0(Windows_NT_10.0;_Win64;_x64;_rv:76.0)_Gecko/20100101_Firefox/76.0</navegador><sku>IMPPREDIAL</sku><url>http://187.217.66.205:99/api/infraccion</url></bancoazteca>"
		
		return url
	def getAfiliacion(self):
		return self.baz_afiliacion


	def encrypt_with_AES(self, message):
		passs = base64.b64decode(self.secret_key.encode('utf-8'))
		iv_ = base64.b64decode(self.iv.encode('utf-8'))
		message = self.pad(message)
		cipher = AES.new(passs, AES.MODE_CBC, iv_)
		cipher_bytes = base64.b64encode(cipher.encrypt(message))
		return bytes.decode(cipher_bytes)


	def decrypt_with_AES(self, encoded):
		passs = base64.b64decode(self.secret_key.encode('utf-8'))
		iv_ = base64.b64decode(self.iv.encode('utf-8'))
		cipher_text = base64.b64decode(encoded.encode('utf-8'))
		#iv = cipher_text[:AES.block_size]
		cipher = AES.new(passs, AES.MODE_CBC, iv_)
		plain_bytes = cipher.decrypt(cipher_text[self.block_size:])
		xml = str(plain_bytes) 
		return xml

	def getTag(self, tag, xml):
		#value = self.getTag("descripcion_codigo", xml)
		tag_apertura = "<"+tag+">"
		tag_cierre = "</"+tag+">"
		n1 = xml.index(tag_apertura)
		n2 = xml.index(tag_cierre)
		return xml[ int(n1) + len(tag_apertura)  : int(n2)]


class TxBaz(models.Model):
	_inherit = 'payment.transaction'

	baz_txn_type = fields.Char('Transaction type')
	baz_txn_status = fields.Char('Approval baz')
	@api.model
	def _handle_feedback_data(self, provider,data):

		tx = super()._handle_feedback_data(provider, data)
		if provider != 'baz':
			return tx

		_logger.warning("OOP1")
		xml_encrypt = data.get('doc').replace(" ","+")
		self_request = self.env['payment.acquirer'].sudo()
		if xml_encrypt:
			xml = PaymentAcquirerBaz.decrypt_with_AES(self_request, xml_encrypt)
			autorizacion = PaymentAcquirerBaz.getTag(self_request, "autorizacion", xml)
			codigo_operacion = PaymentAcquirerBaz.getTag(self_request, "codigo_operacion", xml)
			descripcion_codigo = PaymentAcquirerBaz.getTag(self_request, "descripcion_codigo", xml)
			errorFlujo = PaymentAcquirerBaz.getTag(self_request, "errorFlujo", xml)
			folio = PaymentAcquirerBaz.getTag(self_request, "folio", xml)
			idTransaccion = PaymentAcquirerBaz.getTag(self_request, "idTransaccion", xml)
			monto = PaymentAcquirerBaz.getTag(self_request, "monto", xml)
			reference = PaymentAcquirerBaz.getTag(self_request, "referencia", xml)


		_logger.warning("Reference "+str(data))
		_logger.warning("codigo_operacion "+str(codigo_operacion))
		_logger.warning("idTransaccion "+str(idTransaccion))
		if not idTransaccion:
		   error_msg = _('BAZ: received data with missing reference (%s)') % (idTransaccion)
		   _logger.info(error_msg)
		   raise ValidationError(error_msg)
		
		if codigo_operacion == "00" and idTransaccion:
			_logger.info(descripcion_codigo)
			#raise ValidationError(descripcion_codigo)

		# find tx -> @TDENOTE use txn_id ?
		txs = self.env['payment.transaction'].search([('reference', '=', idTransaccion)])
		if not txs or len(txs) > 1:
		   error_msg = 'Baz: received data for reference %s' % (idTransaccion)
		   if not txs:
		       error_msg += '; no order found'
		   else:
		       error_msg += '; multiple order found'
		   _logger.info(error_msg)
		   raise ValidationError(error_msg)
		return txs[0]

	def _baz_form_get_invalid_parameters(self, data):
		_logger.warning("OOP2")   

	def _baz_form_validate(self, data):
		
		xml_encrypt = data.get('doc').replace(" ","+")
		self_request = self.env['payment.acquirer'].sudo()
		if xml_encrypt:
			xml = PaymentAcquirerBaz.decrypt_with_AES(self_request, xml_encrypt)
			autorizacion = PaymentAcquirerBaz.getTag(self_request, "autorizacion", xml)
			codigo_operacion = PaymentAcquirerBaz.getTag(self_request, "codigo_operacion", xml)
			descripcion_codigo = PaymentAcquirerBaz.getTag(self_request, "descripcion_codigo", xml)
			errorFlujo = PaymentAcquirerBaz.getTag(self_request, "errorFlujo", xml)
			folio = PaymentAcquirerBaz.getTag(self_request, "folio", xml)
			idTransaccion = PaymentAcquirerBaz.getTag(self_request, "idTransaccion", xml)
			monto = PaymentAcquirerBaz.getTag(self_request, "monto", xml)
			reference = PaymentAcquirerBaz.getTag(self_request, "referencia", xml)
		if codigo_operacion == '00':
			status = "Completed"
		else:
			status = "Failed"
		former_tx_state = self.state
		res = {
		    'acquirer_reference': reference,
		    'baz_txn_type': "Baz",
		    
		}
		

		if codigo_operacion == '00' and status in ['Completed', 'Processed', 'Pending']:
		    template = self.env.ref('payment_baz.mail_template_baz_invite_user_to_configure', False)
		    if template:
		        render_template = template.render({
		            'acquirer': self.acquirer_id,
		        }, engine='ir.qweb')
		        mail_body = self.env['mail.thread']._replace_local_links(render_template)
		        mail_values = {
		            'body_html': mail_body,
		            'subject': _('Add your baz account to Odoo'),
		            'email_to': self.acquirer_id.baz_email_account,
		            'email_from': self.acquirer_id.create_uid.email
		        }
		        self.env['mail.mail'].sudo().create(mail_values).send()

		if status in ['Completed', 'Processed']:
		#if 1==1:
		    try:
		        # dateutil and pytz don't recognize abbreviations PDT/PST
		        tzinfos = {
		            'PST': -8 * 3600,
		            'PDT': -7 * 3600,
		        }
		        date = dateutil.parser.parse(data.get('payment_date'), tzinfos=tzinfos).astimezone(pytz.utc).replace(tzinfo=None)
		    except:
		        date = fields.Datetime.now()
		    res.update(date=date)
		    self._set_transaction_done()
		    if self.state == 'done' and self.state != former_tx_state:
		        _logger.info('Validated baz payment for tx %s: set as done' % (self.reference))
		        return self.write(res)
		    return True
		elif status in ['Pending', 'Expired','Failed']:
		    res.update(state_message=data.get('pending_reason', ''))
		    self._set_transaction_pending()
		    if self.state == 'pending' and self.state != former_tx_state:
		        _logger.info('Received notification for baz payment %s: set as pending' % (self.reference))
		        return self.write(res)
		    return True
		else:
		    error = 'Received unrecognized status for baz payment %s: %s, set as error' % (self.reference, status)
		    res.update(state_message=error)
		    self._set_transaction_cancel()
		    if self.state == 'cancel' and self.state != former_tx_state:
		        _logger.info(error)
		        return self.write(res)
		    return True

	def _get_specific_rendering_values(self, processing_values):
		res = super()._get_specific_rendering_values(processing_values)

		if self.provider != 'baz':
			return res
		
		base_url = self.acquirer_id.get_base_url()
		#process_url=urls.url_join(base_url,self.acquirer_id.baz_get_form_action_url())
		#process_url='https://www.puntoazteca.com.mx/BusinessPAYWeb/RealizaVenta?doc=ViAwY+Ykr8LueyrwUPNtNOcXbT1OvcDa3D7ePBrZCbDyWFju/ELcW+NkrSE7sQ4uWGjbp7Vfc2FhkK/ok3cw+kV7UAmNdWh38Add3t3SuhXkg6O95AYYVYbNdCVhNF6sa8m9/5KakB8va7tsWYkTnfpbJOXCv2AKe0phqJP0B1y5IYX383JKDMT6/RI3nQLU6zJOQKSYmWamcSauwjHlOXnihheYdbJ+HK1gBgYrcff9ecUWqUr40fDL1Xk+lPKdi9EPEalP1GCmn7kiXKWdgy0j5Y2cyiIV/8TT651+wvUiJUSqA8iPFdENYxUqQbG8d/rlo3zU/RnvQs6DU+2kq0JnYq9fYuc1vOu6zQk0RkEk2mEvpA28NwzjDMpuO9Z8UQOVygRsnypXQlPshDFyVP2z+zVnXst7ttfsssTfKrmOS7j2GGC0TJiwe6/HXxuGXlfomNYc7npyrMsEZjnyI2yhvfPYkQ6WPX/qTq2ZQ2f7faf4bVGAtDyRmDCjbEWJ5gJRxfJ8/ltAUxfvC+JWVzB5775sSS3lorFhOhphWEPYDdfWcAyji2aDnSDt2Lsrr9NXx4VAxtTFOdfYpdk7whL/Fgq/gx6O2A3mRlXAMo2dZgHHTzra1zJ1K6PqgvOsNrGZFBht8xMom7if0HQJ3bdRoGIHsIIL9gca8X/9SVuV11/mDPFVGiFEROMFkVmmBwxvrCcjZQBJ5qO03sZoHnc1qk2VNGprRTVaXJJi4SM='
		a=BazController.baz_param_request()
		process_url=self.baz_process_url(a['nav'],a['ip_address'],a['url_procedencia'],a['data'])
		partner_first_name, partner_last_name = payment_utils.split_partner_name(self.partner_name)
		return_url=urls.url_join(base_url,'/payment/baz/ipn/')

		return {
		##	'cmd': '_xclick',
			#'api_url' : 'https://testcheckout.buckaroo.nl/html/',
			'api_url': process_url,
			'business': self.acquirer_id.baz_afiliacion,
			'item_name': f"{self.company_id.name}: {self.reference}",
			'item_number': (self.reference),
			'amount': self.amount,
			'currency_code': self.currency_id.name,
			'address1': self.partner_address,
			'city': self.partner_city or None,
			'country': self.partner_country_id.code  or '',
			'state': self.partner_state_id.name or '',
			'email': self.partner_email,
			'zip_code': self.partner_zip,
			'first_name': partner_first_name,
			'last_name': partner_last_name,
			'return_url': return_url,
			#'return_url': '/payment/baz/validate',
			#'notify_url': 'https://www.google.com',
			#'cancel_return': 'https://www.google.com',
			#'api_url': self.acquirer_id.getUrl('request'),
			

			#'handling': '%.2f' % baz_tx_values.pop('fees', 0.0) if self.fees_active else False,
			#'custom': json.dumps({'return_url': '%s' % baz_tx_values.pop('return_url')}) if baz_tx_values.get('return_url') else False,
		}
	
	def baz_process_url(self,nav,ip_address,url_procedencia,data):

		tipo_operacion = 'ecommerce3D'
		amount = str(self.amount)
		email = self.partner_email
		item_number = (self.reference)
		item_name = f"{self.company_id.name}: {self.reference}"
		afiliacion = self.acquirer_id.baz_afiliacion
		id_sesion, id_transaccion = self.acquirer_id.getSession(item_number)

		if amount and email and item_number and item_name and id_transaccion and ip_address and url_procedencia and data:
			size_amount = len(amount)
			num = ""
			_logger.warning('Amount = ' + str(amount))
			_logger.warning('item_name = ' + str(item_name))
			_logger.warning('item_number = ' + str(item_number))
			if '.' in amount:
				amountArr = amount.split(".")
				part1 = amountArr[0]
				part2 = amountArr[1]
				if len(part2) == 1:
					part2 = part2 + "0"
				elif len(part2) == 0:
					part2 = part2 + "00"
				elif len(part2) > 2:
					part2 = part2[0:2]
				
				ceros = 15 - len(part1)
				for i in range(ceros):
					num = num + "0"
				num = num + str(part1) + str(part2)
				url = self.acquirer_id.getUrl("request")
				sku = "Venta en linea para el pedido " + str(item_number)
				params =  '<bancoazteca><tipoOperacion>'+tipo_operacion+'</tipoOperacion><correoComprador>'+str(email)+'</correoComprador><idSesion>'+str(id_sesion)+'</idSesion><idTransaccion>'+str(id_transaccion)+'</idTransaccion><afiliacion>'+str(afiliacion)+'</afiliacion><monto>'+str(num)+'</monto><ipComprador>'+str(ip_address)+'</ipComprador><navegador>'+str(nav)+'</navegador><sku>'+str(sku)+'</sku><url>'+str(url_procedencia)+'</url></bancoazteca>'
				url_final = url + self.acquirer_id.encrypt_with_AES(params)
				return url_final