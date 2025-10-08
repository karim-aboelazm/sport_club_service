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
        'mail',
        'product',
        'account',
        'payment',
        'sale',
    ],

    'data': [
        'security/club_sport_security.xml',
        'security/ir.model.access.csv',
        'data/ir.sequence.xml',
        'data/ir_cron_data.xml',
        'views/res_partner_inherit_view.xml',
        'views/res_users_inherit_view.xml',
        'views/sport_club_model_view.xml',
        'views/sport_club_sport_view.xml',
        'views/sport_club_policy_view.xml',
        'views/sport_club_facility_view.xml',
        'views/sport_club_calendar_view.xml',
        'views/sport_club_pricing_rule_views.xml',
        'views/sport_club_promotion_views.xml',
        'views/sport_club_equipments_view.xml',
		'views/sport_club_reservation_views.xml',
		'views/sport_club_trainer_views.xml',
		'views/sport_club_training_session_views.xml',
        'views/sport_club_equipment_booking_views.xml',
        'wizard/generate_calendar_times_view.xml',
		'views/menus.xml',
],

    'application': True,

    'installable': True,

    'auto_install': False,
}
