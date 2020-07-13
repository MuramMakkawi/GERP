# -*- coding: utf-8 -*-
{
    'name': "HR Payroll Custom",

    'summary': """
        """,

    'description': """
        
    """,

        'author': "Muram Makkawy Mubark",

    'category': 'Human Resource',
    'version': '0.1',
    'depends': ['hr_payroll'],

    
    'data': [
        'security/hr_payroll_custom_security.xml',
        'views/hr_payslip_view.xml',
        'views/salary_rule.xml',
        'views/hr_department_view.xml',
        'wizard/hr_payroll_payslips_by_employees_views_inherit.xml',

    ],
}
