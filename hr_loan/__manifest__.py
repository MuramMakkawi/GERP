# -*- coding: utf-8 -*-

{
    'name': 'HR Loan',
    'author': "Muram Makkawy Mubark",
    'category': 'Human Resource',
    'description': """

	""",

    'depends': ['hr_payroll_custom','voucher_custom'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_loan_security.xml',
        'security/hr_employee_security.xml',
        'sequences/hr_loan_sequence.xml',
        'views/hr_employee_view.xml',
        'data/loan_payroll.xml',
        'views/hr_loan_view.xml',
        'views/hr_payroll_view.xml',
        'views/loan_report.xml',
        'views/reports.xml',
        'views/salary_advance.xml',
        'views/salary_reports.xml',
        'views/res_config_settings.xml',
        'views/loan_payment_view.xml',
        'data/loan_template.xml',
        'data/salary_advance_template.xml',
    ],

    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
