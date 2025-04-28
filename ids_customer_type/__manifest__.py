# -*- coding: utf-8 -*-
{
    'name': "Customer Type",
    'summary': """
       Customer Type
       """,
    'description': """
        Customer Type
    """,
    'author': "IDS",
    'website': "https://www.yourcompany.com",
    'version': '16',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/sales_report.xml',
    ],
}
