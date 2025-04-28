{
    'name': 'Ageing report',
    'version': '1.0.0',
    'category': '',
    'author': 'ids',
    'summary': 'ageing report',
    'description': """ageing report""",
    'depends': ['base', 'account', 'sale', 'report_xlsx', 'ids_partner_filter'],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'wizard/ageing_report_wizard.xml',

    ],
    'license': 'OEEL-1',

    'demo': [],
    'application': True,
    'auto_install': False,
    'assets': {},
}
