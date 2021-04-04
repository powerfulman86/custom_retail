# -*- coding: utf-8 -*-
{
    'name': "custom_retail",
    'summary': """custom_retail""",
    'description': """custom_retail""",
    'author': "CubicIt Egypt",
    'category': 'other',
    'version': '0.1',
    'depends': ['base', 'sale', 'purchase', 'stock', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase.xml',
        'views/sale.xml',
        'views/account.xml',
        'views/stock.xml',
        'views/menu.xml',
    ],
}
