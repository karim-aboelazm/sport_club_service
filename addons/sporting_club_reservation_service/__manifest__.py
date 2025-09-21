# -*- coding: utf-8 -*-
{
    'name': "Sporting Club Reservation Service",

    'summary': "Manage reservations, memberships, and scheduling for sporting clubs.",

    'description': """
        Sporting Club Reservation Service
        =================================
        
        This module allows sporting clubs to manage:
        
        - Member profiles and subscriptions
        - Facility reservations (courts, fields, halls, etc.)
        - Scheduling and availability
        - Reservation payments and invoices
        - Usage reporting and analytics
        
        It aims to streamline club operations and improve customer experience.
    """,

    'author': "Karim Mohammed Aboelazm",

    'website': "https://www.yourcompany.com",

    'license': "LGPL-3",

    'category': 'Services/Reservation',

    'version': '0.1',

    'depends': [
        'base',
        'contacts',
        'base_cities',
        'mail'
    ],

    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'views/res_partner_inherit_view.xml',
        'views/sport_club_model_view.xml',
        'views/sport_club_sport_view.xml',
        'views/sport_club_policy_view.xml',
        'views/sport_club_facility_view.xml',
        'views/sport_club_calendar_view.xml',
    ],

    'application': True,

    'installable': True,

    'auto_install': False,
}
