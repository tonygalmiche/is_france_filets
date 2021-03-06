# -*- coding: utf-8 -*-
{
    'name'     : u'InfoSaône - Module Odoo pour France Filets',
    'version'  : '0.1',
    'author'   : u'InfoSaône',
    'category' : u'InfoSaône',


    'description': u"""
InfoSaône - Module Odoo pour France Filets
===================================================
""",
    'maintainer' : u'InfoSaône',
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
        'security/res.groups.xml',
        'security/ir.model.access.csv',
        'security/ir.model.access.xml',
        'views/assets.xml',
        'views/res_company_view.xml',
        'views/partner_view.xml',
        'views/sale_view.xml',
        'views/account_invoice_view.xml',
        'views/is_export_compta_view.xml',
        'views/is_sale_order_line.xml',
        'views/is_account_invoice_line.xml',
        'views/is_filet_view.xml',
        'views/is_suivi_budget_view.xml',
        'views/menu.xml',
        'report/sale_report_templates.xml',
        'report/report_invoice.xml',
        'report/planning_report_templates.xml',
        'report/fiche_travail_report_templates.xml',
        'report/pv_reception_report_templates.xml',
        'report/is_suivi_budget_report_templates.xml',
        'report/is_suivi_budget_journal_vente_report_templates.xml',
        'report/layouts.xml',
        'report/report.xml',
    ],
    'installable': True,
    'application': True,
    'qweb': [
    ],
}

