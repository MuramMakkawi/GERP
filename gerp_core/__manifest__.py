# -*- coding: utf-8 -*-

{
    'name': 'GERP Core',
    'author': 'Genext IT',
    'summary': 'Core application for GERP modules.',
    'version': '1.0',
    'category': 'GERP',
    'description': """
GERP Core
========
""",
    'depends': ['base_setup', 'account', 'sale', 'purchase', 'stock', 'hr_expense','hr_payroll'],
    'data': [
        'security/core_security.xml',
        'views/main_menu.xml',
        'views/hr_departmen_view.xml',
        'views/res_users_view.xml',
    ],
}
