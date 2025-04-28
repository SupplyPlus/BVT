# -*- coding: utf-8 -*-
{
    'name': "Access Right",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'version': '0.1',
    'depends': ['base', 'product', 'sale', 'sale_margin'],

    'data': [
        'security/groups.xml',
        'views/product.xml',
        'views/sales_order.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
