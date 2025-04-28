# -*- coding: utf-8 -*-
{
    'name': "Custom Invoices Report",
    'description': """
        Long description of module's purpose
    """,
    'author': "IDS",
    'version': '16',
    'depends': ['base', 'account', 'ids_partner_filter', 'l10n_sa'],
    'license': 'AGPL-3',
    'data': [
        'reports/invoice_report_action.xml',
        'reports/invoice_report_template.xml',
        'reports/external_layout_boxed.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
