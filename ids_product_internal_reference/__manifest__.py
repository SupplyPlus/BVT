# -*- coding: utf-8 -*-


{
    'name': 'IDS - Product Internal Reference',
    'version': '13.0.0.1.0',
    'category': 'Product',
    'description': """Generate internal ref by category prefix and starting number""",
    'author': 'IDS',
    'website': 'http://www.idsc-sa.com',
    'depends': ['base', 'product', 'sale', 'purchase', 'ids_api_customisations', 'stock'],
'license': 'AGPL-3',
    'data': [
        'data/sequence_data.xml',
        'views/product_category.xml',
        'views/product_tag_view.xml',
        'views/product_segment_view.xml',
        'views/product_view.xml'
    ],
}
