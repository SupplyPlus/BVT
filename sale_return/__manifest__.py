{
    'name': 'Sale return',
    'summary': 'Create return stock from Sale Order',
    'category': 'Sale',
    'version': '12.0.1.0.1',
    'author': 'IDS',
    'website': 'https://www.trey.es',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'base',
        'sale',
        'sale_stock',
        'sale_enterprise',
        'web',

    ],
    'data': [
        'data/ir_sequence.xml',
        'report/sale_return_report.xml',
        'views/sale_order.xml',
        'views/stock_warehouse.xml',
    ],
    # 'post_init_hook': '_create_warehouse_return_data',

}
