# -*- coding: utf-8 -*-
{
    'name': "Portal Customisation",
    'description': """ Add buttons to confirm the purchase order and view the receipt. """,
    'author': "IDS",
    'website': "",
    'category': '',
    'version': '16.0',
    'depends': ['base', 'web', 'portal', 'purchase', 'stock', 'sale', 'l10n_gcc_invoice', 'account'],
    'data': [
        'views/portal_template.xml',
        # 'views/purchase_order.xml',
        # 'views/stock_picking.xml',
        'reports/report_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ids_portal_customisation/static/src/js/purchase_confirm.js',
        ],
    },
    'demo': [
    ],
}
