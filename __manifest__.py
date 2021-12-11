# -*- coding: utf-8 -*-
{
    'name': "custom_retail",
    'summary': """custom_retail""",
    'description': """custom_retail""",
    'author': "CubicIt Egypt",
    'category': 'other',
    'version': '0.1',
    'depends': ['base', 'contacts', 'sale', 'purchase', 'stock', 'account', 'calendar',
                'board'],

    # always loaded
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/stock_packing.xml',
        'views/menu.xml',
        # 'views/partner.xml',
        'views/driver.xml',
        'views/invoice.xml',
        'views/sale.xml',
        'views/product_template_views.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
