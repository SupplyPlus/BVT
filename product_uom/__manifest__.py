# -*- coding: utf-8 -*-
{
    'name': 'DGTERA Product Uom',
    'summary': """Enhance Product Uom""",
    'version': '14.0.0.1.0',
    'author': 'IDS',
    'company': 'DGTERA',
    "website": "http://dgtera.com",
    'category': 'Warehouse',
    'depends': ['product', 'ids_product_internal_reference', 'ids_access_right'],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/product_category.xml',
        'views/product_template_view.xml',
        'views/sales_report.xml',
        'data/ir_cron.xml',
    ],

}
