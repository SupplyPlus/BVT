# -*- coding: utf-8 -*-
{
    'name': "Accounting Updates",
    'summary':
        """
        Add column In Partner Ledger ( Bill Ref )
        """,
    'version': '15',
    'author': 'IDS',
    'depends': ['base', 'account', 'account_reports', 'ids_partner_filter'],
    'data': [
        'views/partner_leger_form.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
