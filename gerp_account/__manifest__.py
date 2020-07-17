# -*- coding: utf-8 -*-
{
    'name': "GERP Account",

    'summary': """Account""",

    'description': """
       Account Custome
    """,

    'author': "Muram Makkawy Mubarak",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoice',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/account_security.xml',
    ],
  
}