# -*- coding: utf-8 -*-
{
    'name': "GERP Inventory",
    'summary': """Inventory custome""",
    'description': """
        Inventory custome """,
    'author': "Muram Makkawy Mubarak",
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['gerp_core'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/stock_secutiry.xml',
        'views/stock_warehouse_view.xml',
        'views/stock_location_view.xml'
    ],

}