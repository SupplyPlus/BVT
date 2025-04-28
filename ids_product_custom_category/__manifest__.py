# -*- coding: utf-8 -*-
{
    'name': "Product Custom Category",
    'description': """
        Long description of module's purpose
    """,

    'author': "IDS",
    'website': "https://www.yourcompany.com",
    'version': '0.1',
    'depends': ['base', 'stock', 'product'],
'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/app_segment.xml',
        'views/product.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
