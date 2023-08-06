# -*- coding: utf-8 -*-
{
    'name': "crm_metadata_rest_api",

    'summary': """
        Expose CRM Metadata on the Rest API""",

    'author': "Coopdevs Treball SCCL",
    'website': "",

    'category': 'api',
    'version': '14.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'crm_metadata',
        'crm_rest_api'
    ],

    # always loaded
    'data': [],
    # only loaded in demonstration mode
    'demo': [],
}
