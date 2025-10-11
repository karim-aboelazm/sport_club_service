# -*- coding: utf-8 -*-
import base64
import io
import pytz
from io import BytesIO
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import xlsxwriter


# -------------------------------------------------------------------------
# Excel Styling & Layout Helpers
# -------------------------------------------------------------------------

def _get_excel_formats(workbook):
    return {
        'top_header_titles': workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#ABAFB1',
            'font_size': 14,
            "font_name": "Aptos Narrow"
        }),
        'top_header_data': workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 12,
            "font_name":"Aptos Narrow"
        }),
        'report_name_format': workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_name':"Aptos Narrow",
            "font_size":18,
            'bg_color': '#ABAFB1',
        }),
        'table_header_format': workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#ABAFB1',
            'font_size': 14,
            "font_name": "Aptos Narrow"
        }),
        'table_body_format': workbook.add_format({
            "font_name": "Aptos Narrow",
            'border': 1,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
        }),
    }

def _render_excel_top_header(ws, formats, obj, date_from, date_to):
    """
    Draw the top header section with company logo, user, date, and filters.
    """
    user_tz = obj.env.user.tz or obj.env.context.get('tz')
    user_pytz = pytz.timezone(user_tz) if user_tz else pytz.utc
    current_datetime = (datetime.now().astimezone(user_pytz).replace(tzinfo=None)).strftime('%d/%m/%Y %I:%M %p')

    # Align columns width
    [ws.set_column(i, i + 1, 20) for i in range(8)]

    ws.merge_range("A2:B2", _("Current Date"), formats['top_header_titles'])
    ws.merge_range("A3:B3", _("Current User"), formats['top_header_titles'])

    ws.merge_range("C2:D2", current_datetime, formats['top_header_data'])
    ws.merge_range("C3:D3", obj.env.user.name, formats['top_header_data'])

    if date_from and date_to:
        ws.merge_range("A4:B4", _("Date From"), formats['top_header_titles'])
        ws.merge_range("A5:B5", _("Date To"), formats['top_header_titles'])

        ws.merge_range("C4:D4", date_from.strftime('%d/%m/%Y'), formats['top_header_data'])
        ws.merge_range("C5:D5", date_to.strftime('%d/%m/%Y'), formats['top_header_data'])

    # --- Company logo ---
    if obj.env.company.logo:
        buf_image = BytesIO(base64.b64decode(obj.env.company.logo))
        ws.insert_image(
            'B2',
            'company_logo.png',
            {
                'image_data': buf_image,
                'x_offset': 1,
                'y_offset': 1,
                'x_scale': 0.15,
                'y_scale': 0.15,
                'object_position': 2
            }
        )

def _render_excel_report_name(ws, formats,header, report_name):
    ws.merge_range(6, 0, 7, len(header) - 1, report_name, formats['report_name_format'])

def _render_excel_table_header(ws, formats, header):
    for col, val in enumerate(header):
        ws.set_column(col, col, len(str(val)) + 10)
        ws.set_row(9, 30)
        ws.write(9, col, val, formats['table_header_format'])

def _render_excel_table_body(ws, formats ,body):
    for row_index, row_values in enumerate(body, start=10):
        ws.set_row(row_index,25)
        for col_index, val in enumerate(row_values):
            ws.write(row_index, col_index, str(val) if val is not None else '',formats['table_body_format'])

# -------------------------------------------------------------------------
# Abstract Excel Report Base
# -------------------------------------------------------------------------

class BaseExcelReportWizard(models.AbstractModel):
    _name = 'base.excel.report.abstract'
    _description = 'Abstract Base Excel Report'

    # ---------------------------------------------------------------------
    # Fields
    # ---------------------------------------------------------------------
    date_from = fields.Date(
        string="From Date"
    )
    date_to = fields.Date(
        string="To Date"
    )
    export_format = fields.Selection(
        selection=[
            ('pdf', 'PDF'),
            ('xlsx', 'Excel')
        ],
        string="Export Format",
        required=True,
        default='pdf'
    )
    excel_worksheet = fields.Binary(
        string='Download Report',
        readonly=True,
        help="The generated Excel report as a downloadable file."
    )

    # ---------------------------------------------------------------------
    # Abstract Methods (to be implemented by child models)
    # ---------------------------------------------------------------------
    def _prepare_domain_to_get_data(self):
        raise NotImplementedError

    def _prepare_all_data_based_on_domain(self, domain):
        raise NotImplementedError

    def _prepare_report_header(self):
        raise NotImplementedError

    def _map_record_to_row(self, record):
        raise NotImplementedError

    # ---------------------------------------------------------------------
    # Core Logic
    # ---------------------------------------------------------------------
    def _prepare_report_body(self, records):
        """
        Convert records into a list of rows, validating against header length.
        """
        header = self._prepare_report_header()
        body = []

        for rec in records:
            row = self._map_record_to_row(rec)
            if len(row) != len(header):
                raise UserError(
                    _("Header length (%s) does not match row length (%s) for record %s")
                    % (len(header), len(row), rec.display_name)
                )
            body.append(row)
        return body

    def _get_report_name(self):
        """
        Override this in child models for dynamic naming.
        """
        return self._description or 'Excel Report'

    def _prepare_full_report_data(self):
        domain = self._prepare_domain_to_get_data()
        records = self._prepare_all_data_based_on_domain(domain)
        if not records:
            raise UserError(_("No records found for the selected criteria."))

        return {
            'header': self._prepare_report_header(),
            'body': self._prepare_report_body(records),
            'report_name': self._get_report_name(),
            'start_date': getattr(self, 'date_from', False),
            'end_date': getattr(self, 'date_to', False),
            **self._additional_data()
        }

    def _get_pdf_report_id(self):
        return

    def _prepare_pdf_action(self,ref_id):
        action = self.env.ref(ref_id)
        return action.report_action(self)

    def _additional_data(self):
        return {}
    # ---------------------------------------------------------------------
    # Excel Export
    # ---------------------------------------------------------------------
    def action_print_excel(self, header,body, report_name, date_from=None, date_to=None):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(report_name)

        formats = _get_excel_formats(workbook)
        _render_excel_top_header(worksheet,formats,self,date_from,date_to)
        _render_excel_report_name(worksheet,formats,header,report_name)
        _render_excel_table_header(worksheet,formats,header)
        _render_excel_table_body(worksheet,formats,body)

        workbook.close()
        output.seek(0)

        self.excel_worksheet = base64.encodebytes(output.read())

        return {
            'type': 'ir.actions.act_url',
            'name': report_name,
            'url': f'/web/content/{self._name}/{self.id}/excel_worksheet/{report_name}.xlsx?download=true',
            'target': 'new'
        }

    def action_print_report(self):
        self.ensure_one()
        report_data = self._prepare_full_report_data()
        report_name = self._get_report_name()
        if self.export_format == 'pdf':
            ref_id = self._get_pdf_report_id()
            return self._prepare_pdf_action(ref_id)
        else:
            return self.action_print_excel(report_data['header'],report_data['body'], report_name, self.date_from, self.date_to)
