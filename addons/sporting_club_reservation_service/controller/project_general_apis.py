# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
from .utils import *

class GeneralApiController(http.Controller):

    @http.route('/api/general/all', type='http', auth='public', methods=['GET'], csrf=False, save_session=False, cors="*")
    def get_all_general_data(self):
        try:
            api_model = request.env['project.general.api'].sudo()
            result = api_model.fetch_all_data()
            return valid_response(code=200, message="Success", body=result)
        except ValidationError as e:
            return error_response(code=404, message=str(e))
        except Exception as e:
            return error_response(code=404, message="Unexpected error: %s" % str(e))

    @http.route('/api/models/all', type='http', auth='public', methods=['GET'], csrf=False, save_session=False, cors="*")
    def get_all_models_fields(self):
        try:
            Model = request.env['ir.model'].sudo()
            Field = request.env['ir.model.fields'].sudo()
            result = []
            excluded_models = ["mail.thread", "mail.activity.mixin"]
            excluded_field_names = [
                "id", "create_date", "write_date", "create_uid", "write_uid",
                "has_message", "message_attachment_count", "message_follower_ids",
                "message_has_error", "message_has_error_counter", "message_has_sms_error",
                "message_ids", "message_is_follower", "message_needaction",
                "message_needaction_counter", "message_partner_ids",
                "my_activity_date_deadline", "rating_ids", "website_message_ids",
                "activity_calendar_event_id", "activity_date_deadline",
                "activity_exception_decoration", "activity_exception_icon",
                "activity_ids", "activity_state", "activity_summary",
                "activity_type_icon", "activity_type_id", "activity_user_id"
            ]
            for model_rec in Model.search([('model','in',get_all_models()),('model','not in',excluded_models)]):
                model_data = {
                    'model': model_rec.model,
                    'name': model_rec.name,
                    'fields': []
                }

                for field in Field.search([('model_id', '=', model_rec.id)]):
                    # Skip excluded models
                    if field.model in excluded_models:
                        continue

                    # Skip excluded fields
                    if field.name in excluded_field_names:
                        continue

                    field_data = {
                        'name': field.name,
                        'type': field.ttype,
                    }
                    if field.ttype in ['many2one', 'many2many', 'one2many']:
                        field_data['related'] = field.relation

                    if field.ttype == 'selection':
                        sel = field.selection
                        if callable(sel):
                            sel = sel()
                        if isinstance(sel, str):
                            import ast
                            sel = ast.literal_eval(sel)
                        field_data['selection'] = [s[0] for s in sel]

                    if field.ttype in ['date', 'datetime']:
                        field_data['format'] = 'YYYY-MM-DD' if field.ttype == 'date' else 'YYYY-MM-DD HH:MM:SS'

                    model_data['fields'].append(field_data)

                result.append(model_data)

            return valid_response(code=200, message="Success", body=result)

        except Exception as e:
            return error_response(code=404, message=str(e))