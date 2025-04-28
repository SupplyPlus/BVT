# -*- coding: utf-8 -*-
##############################################################################


{
    'name': 'Api customisation',
    'version': '1.0',
    'category': 'Product',
    'author': '',
    'website': '',
    'description': """
        Api customisation
    """,

    'depends': ['base', 'product', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/server_actions.xml',
        'views/product_template_inherit.xml',
        'views/sale_order_views.xml',
        'views/brand_view.xml',
        'views/segment_view.xml',
        'views/driver_view.xml',
        'views/product_category_views.xml',
        'views/product_sub_category.xml',
        'views/product_attribute_view.xml',
        'wizard/api_call_wizard.xml'

    ],
    'installable': True,
}
