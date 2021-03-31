# -*- coding: utf-8 -*-
{
    'name': "custom_retail",
    'summary': """custom_retail""",
    'description': """custom_retail""",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'sale', 'purchase', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/menu.xml',
        'views/purchase.xml',
        'views/sale.xml',
    ],
}
