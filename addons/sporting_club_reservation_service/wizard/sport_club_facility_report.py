# -*- coding: utf-8 -*-
from odoo import models, fields, _

class ClubFacilitiesReportWizard(models.TransientModel):
    _name = 'report.sport.club.facilities.wizard'
    _inherit = 'base.excel.report.abstract'
    _description = 'Club Facilities Report Wizard'

    club_id = fields.Many2one(
        comodel_name='sport.club.model',
        string='Club'
    )
    facility_type = fields.Selection(
        selection=[
            ('court', 'Court'),
            ('gym', 'Gym'),
            ('pool', 'Pool'),
            ('other', 'Other')
        ],
        string='Facility Type'
    )
    sport_id = fields.Many2one(
        comodel_name='sport.club.sports',
        string='Sport'
    )

    def _prepare_domain_to_get_data(self):
        domain = []
        if self.club_id:
            domain.append(('sport_club_id', '=', self.club_id.id))
        if self.facility_type:
            domain.append(('facility_type', '=', self.facility_type))
        if self.sport_id:
            domain.append(('sport_id', '=', self.sport_id.id))
        return domain

    def _prepare_all_data_based_on_domain(self, domain):
        return self.env['sport.club.facility'].search(domain)

    def _prepare_report_header(self):
        return [
            _('Facility Name'),
            _('Club'),
            _('Type'),
            _('Capacity'),
            _('Sport'),
            _('Indoor'),
            _('Surface Type'),
            _('Active')
        ]

    def _map_record_to_row(self, rec):
        return [
            rec.name,
            rec.sport_club_id.name if rec.sport_club_id else '',
            dict(rec._fields['facility_type'].selection).get(rec.facility_type, ''),
            rec.capacity or '',
            rec.sport_id.name if rec.sport_id else '',
            'Yes' if rec.indoor else 'No',
            dict(rec._fields['surface_type'].selection).get(rec.surface_type, ''),
            'Yes' if rec.active else 'No'
        ]

    def _get_report_name(self):
        return _('Club Facilities Report')

    def _get_pdf_report_id(self):
        """
        Return the PDF QWeb report action ID.
        """
        return 'sporting_club_reservation_service.action_report_sport_club_facility_pdf'