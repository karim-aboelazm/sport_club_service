# -*- coding: utf-8 -*-
from odoo import models, fields, _

class ClubsOverviewReportWizard(models.TransientModel):
    _name = 'report.sport.club.overview.wizard'
    _inherit = 'base.excel.report.abstract'
    _description = 'Clubs Overview Report Wizard'

    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country'
    )
    governorate_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Governorate'
    )
    sport_ids = fields.Many2many(
        comodel_name='sport.club.sports',
        string='Sports'
    )

    def _prepare_domain_to_get_data(self):
        domain = [('active', '=', True)]
        if self.country_id:
            domain.append(('country_id', '=', self.country_id.id))
        if self.governorate_id:
            domain.append(('governorate_id', '=', self.governorate_id.id))
        if self.sport_ids:
            domain.append(('sport_ids', 'in', self.sport_ids.ids))
        return domain

    def _prepare_all_data_based_on_domain(self, domain):
        return self.env['sport.club.model'].search(domain)

    def _prepare_report_header(self):
        return [
            _('Club Name'),
            _('Owner'),
            _('Country'),
            _('Governorate'),
            _('City'),
            _('Sports Offered'),
            _('Active')
        ]

    def _map_record_to_row(self, rec):
        return [
            rec.name,
            rec.owner_id.name if rec.owner_id else '',
            rec.country_id.name if rec.country_id else '',
            rec.governorate_id.name if rec.governorate_id else '',
            rec.city_id.name_en if rec.city_id else '',
            ", ".join(rec.sport_ids.mapped('name')),
            'Yes' if rec.active else 'No'
        ]

    def _get_report_name(self):
        return _('Clubs Overview Report')

    def _get_pdf_report_id(self):
        """
        Return the PDF QWeb report action ID.
        """
        return 'sporting_club_reservation_service.action_report_sport_club_overview_pdf'