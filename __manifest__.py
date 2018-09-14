# -*- coding: utf-8 -*-
{
    'name'     : 'InfoSaône - Module Odoo pour France Filets',
    'version'  : '0.1',
    'author'   : 'InfoSaône',
    'category' : 'InfoSaône',


    'description': """
InfoSaône - Module Odoo pour France Filets
===================================================
""",
    'maintainer' : 'InfoSaône',
    'website'    : 'http://www.infosaone.com',
    'depends'    : [
        'base',
        'stock',
        'sale',
        'mail',
        'account',
        'account_accountant',
        'purchase',
        'document',
],
    'data' : [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/partner_view.xml',
        'views/sale_view.xml',
        'views/menu.xml',
        'report/sale_report_templates.xml',
        'report/layouts.xml',
    ],
    'installable': True,
    'application': True,
    'qweb': [
    ],
}

