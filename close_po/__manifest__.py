# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Close Purchase',
    'version': '14.0.1',
    'category': '',
    'summary': 'For all',
    'author': "Adithya",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'description': """
This module is used to identify the PO which are closed
    """,
    'depends': ['base','purchase'],
    'data': [
        'views/close_po.xml'
       
    ],
   
    'installable': True,
    'auto_install': False
}
