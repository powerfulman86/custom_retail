# -*- coding: utf-8 -*-
{
    'name': "custom_retail",
    'summary': """custom_retail""",
    'description': """custom_retail""",
    'author': "CubicIt Egypt",
    'category': 'other',
    'version': '0.1',
    'depends': ['base', 'sale', 'purchase', 'stock', 'account', 'accounting_pdf_reports'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/partner.xml',
        'views/driver.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
