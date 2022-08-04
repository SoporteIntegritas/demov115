# -*- coding: utf-8 -*-
{
    'name': "mx_integritas_payment_baz",
    'summary': """
        Payment Acquirer: BAZ Implementation""",
    'description': """
        Modulo creado para implementar el metodo de pago con banco azteca v13
    """,
    'author': "Integritas",
    'website': "https://integritas.mx",
    'category': 'Accounting/Payment',
    'version': '0.1',
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/templates.xml',
        'views/payment_baz_templates.xml',
        'views/payment_transaction.xml',
        'data/payment_acquirer_data.xml',
    ],
    'application': True,
    'uninstall_hook': 'uninstall_hook',
    'demo': [
        'demo/demo.xml',
    ],
}
