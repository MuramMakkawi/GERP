# -*- coding: utf-8 -*-
{
    'name': "GERP Inventory",

    'summary': """Inventory custome""",

    'description': """
        Inventory custome
    """,

    'author': "Muram Makkawy Mubarak",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['gerp_core'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/stock_secutiry.xml',
        'views/stock_warehouse_view.xml',
    ],
    # only loaded in demonstration mode
    
}