# -*- coding: utf-8 -*-
{
    'name': "Account Partner Statement",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "PerfectTech",
    'contributors': [
        'Ahmed Sakr <odoosaqr@gmail.com>',
    ],
    'website': "http://www.yourcompany.com",
    'version': '0.1',
    'depends': ['base', 'account', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/partner_account.xml',
        'wizards/partner_account_report_action.xml',
        'wizards/partner_account_report_template.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
