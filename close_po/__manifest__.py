# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Close Purchase',
    'version': '14.0.1.6',
    'category': '',
    'summary': 'For all',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'description': """
This module is display the fields .
    """,
    'depends': ['base','purchase'],
    'data': [
        'views/close_po.xml'
       
    ],
   
    'installable': True,
    'auto_install': False
}
