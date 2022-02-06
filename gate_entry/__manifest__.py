# -*- coding: utf-8 -*-
{
    'name': "Security Check",

    'summary': """
        Gate Entry capture by security personnel""",

    'description': """
        The objective of this module is to solve the persistent industry problem of data entry and reporting by the security
        personnel at physical locations. Even today, in major part of the industry, security personnel record all the data in
        ledgers by way of manual entry. This is prone to lot of manual errors, difficulty in report generation, and majorly, 
        the dependency of one department to another in ERP systems will become discontinued at the security department.
        In order to solve these issues and to bring a continuity between various departments of a company and its security
        department, the Gate Entry module has been designed
    """,

    'author': 'Adithya',
    
    'email': 'adithyakulgod@gmail.com',
    'mobile': '9986870937',

    'category': 'Custom',
    'version': '14.0.1',

    'depends': ['base', 'stock', 'purchase', 'sale', 'sale_stock','purchase_stock','fleet','close_po'],

    'data': [
        'data/gate_entry_group_access.xml',
        'security/ir.model.access.csv',
        'views/gate_entry.xml',
        'views/gate_entry_user.xml',
        'views/stock_picking.xml',
        'views/purchase_order.xml',
        # 'views/header_footer.xml',
        # 'views/gateentry_in_report.xml',
        # 'views/gateentry_out_report.xml',
        # 'views/res_config_settings.xml',
    ],

    # 'images': ['static/description/gate.png'],

    
}
