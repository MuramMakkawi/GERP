# -*- coding: utf-8 -*-
{
    'name': "GERP Purchase",

    'summary': """
        GERP Purchase Custome""",

    'description': """
        GERP Purchase Cutome
    """,

    'author': "Muram Makkawy Mubarak",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['gerp_core'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/purchase_security.xml',
        'views/purchase_order_view.xml',
    ],
  
}