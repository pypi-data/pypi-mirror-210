# -*- coding: utf-8 -*-
{
    'name': "crm_rest_api",

    'summary': """
        Expose CRM Lead on the Rest API""",

    'author': "Coopdevs Treball SCCL",
    'website': "",

    'category': 'api',
    'version': '14.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'base_rest',
        'base_rest_base_structure',
        'crm',
        'component'
    ],

    # always loaded
    'data': [],
    # only loaded in demonstration mode
    'demo': [],
}
