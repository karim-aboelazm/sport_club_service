# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReservationRevenueWizard(models.TransientModel):
    """
    Reservation Revenue Report Wizard
    ---------------------------------
    This wizard generates either a PDF or Excel reservation revenue report
    using the standardized BaseExcelReportWizard infrastructure.
    """
    _name = 'reservation.revenue.wizard'
    _inherit = ['base.excel.report.abstract']
    _description = 'Reservation Revenue Report Wizard'

    # ---------------------------------------------------------------------
    # Fields
    # ---------------------------------------------------------------------
    sport_id = fields.Many2one(
        comodel_name='sport.club.sports',
        string="Sport Type"
    )
    club_id = fields.Many2one(
        comodel_name='sport.club.model',
        string="Club"
    )

    # ---------------------------------------------------------------------
    # Domain Preparation
    # ---------------------------------------------------------------------
    def _prepare_domain_to_get_data(self):
        """
        Build the domain to filter reservation records.
        """
        domain = [('state', 'in', ['confirmed', 'checked_in', 'checked_out'])]
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        if self.club_id:
            domain.append(('club_id', '=', self.club_id.id))
        if self.sport_id:
            domain.append(('sport_id', '=', self.sport_id.id))
        return domain

    def _prepare_all_data_based_on_domain(self, domain):
        """
        Fetch the reservation records based on the prepared domain.
        """
        return self.env['sport.club.reservation'].search(domain)

    def _additional_data(self):
        records = self._prepare_all_data_based_on_domain(self._prepare_domain_to_get_data())
        return {
            'sport': self.sport_id.name or "All Sports",
            'club': self.club_id.name or "All Clubs",
            'reservations':len(records),
            'total_taxes':round(sum(r.amount_tax for r in records),2),
            'total_revenues':round(sum(r.amount_total for r in records),2),
        }
    # ---------------------------------------------------------------------
    # Excel Table Mapping
    # ---------------------------------------------------------------------
    def _prepare_report_header(self):
        """
        Define the Excel table headers.
        """
        return [
            _('Date'),
            _('Sport'),
            _('Club'),
            _('Total Revenue'),
            _('Tax'),
            _('Payment Status'),
            _('Reservation Status'),
        ]

    def _map_record_to_row(self, record):
        """
        Convert a reservation record into a table row.
        """
        return [
            record.date.strftime('%Y-%m-%d') if record.date else '',
            record.sport_id.name or '',
            record.club_id.name or '',
            round(record.amount_total, 2),
            f"{round(record.amount_tax, 2)} %" if record.tax_id else "0.0 %",
            dict(record._fields['payment_state'].selection).get(record.payment_state, ''),
            dict(record._fields['state'].selection).get(record.state, ''),
        ]

    # ---------------------------------------------------------------------
    # Report Naming / PDF Action
    # ---------------------------------------------------------------------
    def _get_report_name(self):
        """
        Excel file name.
        """
        return 'Reservation Revenue Report'

    def _get_pdf_report_id(self):
        """
        Return the PDF QWeb report action ID.
        """
        return 'sporting_club_reservation_service.action_report_reservation_revenue_pdf'