# -*- coding: utf-8 -*-
{
    'name': "Country State Cities",

    'summary': "Country State Cities",

    'author': 'Karim Mohammed Aboelazm',

    'category': 'Localization',

    'version': '0.1',

    'license': 'LGPL-3',

    'depends': ['base', 'contacts'],

    'data': [
        'security/ir.model.access.csv',
        'data/cities.xml',
        'views/res_cities.xml',
        'views/res_areas.xml',
        'views/res_zones.xml',
        'views/res_partner.xml',
    ],
    'installable': True,

    'application': True,

    'auto_install': True,

}

