# -*- coding: utf-8 -*-
{
    'name': "crm_sale_order_line_rest_api",

    'summary': """
        Expose CRM order lines on the Rest API""",

    'author': "Coopdevs Treball SCCL",
    'website': "",

    'category': 'api',
    'version': '12.0.0.0.4',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'crm_rest_api',
        'crm_sale_order_line'
    ],

    # always loaded
    'data': [],
    # only loaded in demonstration mode
    'demo': [],
}
