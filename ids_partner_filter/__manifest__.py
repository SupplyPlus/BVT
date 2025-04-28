# -*- coding: utf-8 -*-
{
    'name': "Partner Filter",
    'description': """
        Long description of module's purpose
    """,

    'author': "IDS",
    'website': "https://www.yourcompany.com",
    'version': '0.1',
    'depends': ['base', 'account', 'purchase', 'sale'],
'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/sales_order.xml',
        'views/account_move.xml',
        'views/purchase_order.xml',
        'views/account_payment.xml',
        'views/res_partner.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
