# -*- coding: utf-8 -*-
{
    'name': "crm_sale_order_line_contract_rest_api",

    'summary': """
        Enhance CRM order lines Rest API to add contract specific configs""",

    'author': "Coopdevs Treball SCCL",
    'website': "",

    'category': 'api',
    'version': '12.0.0.0.3',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'crm_sale_order_line_rest_api'
    ],

    # always loaded
    'data': [],
    # only loaded in demonstration mode
    'demo': [],
}
