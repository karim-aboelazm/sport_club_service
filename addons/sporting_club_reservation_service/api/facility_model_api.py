from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, UserError

class SportClubFacility(models.Model):
    _inherit = "sport.club.facility"

    @api.model
    def _api_create_facility(self, vals):
        if not vals.get('sport_club_id'):
            raise ValidationError(_("Sport club is required."))

        data = self._from_api_dict(vals)
        facility = self.sudo().create(data)
        return facility._to_api_dict()

    @api.model
    def _api_search_facilities(self, domain=None, limit=100, offset=0):
        domain = domain or []
        facilities = self.search(domain, limit=limit, offset=offset)
        return [fac._to_api_dict() for fac in facilities]

    @api.model
    def _api_get_facility(self, facility_id):
        facility = self.browse(int(facility_id))
        if not facility.exists():
            raise UserError(_("Facility not found."))
        return facility._to_api_dict()

    @api.model
    def _filter_facilities_with_keywords(self, keyword):
        if not keyword:
            return []

        conditions = [
            ('name', 'ilike', keyword),
            ('sport_club_id.name', 'ilike', keyword),
            ('sport_id.name', 'ilike', keyword),
            ('surface_type', 'ilike', keyword),
            ('facility_type', 'ilike', keyword),
        ]

        domain = ['|'] * (len(conditions) - 1) + conditions
        facilities = self.search(domain)
        return [fac._to_api_dict() for fac in facilities]

    @api.model
    def _api_update_facility(self, vals):
        if 'id' not in vals:
            raise ValidationError(_("Facility ID is required for update."))

        facility = self.browse(int(vals['id']))
        if not facility.exists():
            raise UserError(_("Facility not found."))

        vals.pop('id', None)
        data = self._from_api_dict(vals)
        facility.sudo().write(data)
        return facility._to_api_dict()

    @api.model
    def _api_delete_facility(self, facility_id):
        facility = self.browse(int(facility_id))
        if not facility.exists():
            raise UserError(_("Facility not found."))

        facility.unlink()
        return {"deleted": True, "id": facility_id}

    @api.model
    def _from_api_dict(self, data):
        vals = {}

        simple_fields = ['facility_type', 'capacity', 'indoor','lighting', 'surface_type', 'color', 'active']
        for field in simple_fields:
            if field in data:
                vals[field] = data[field]

        if 'sport_club_id' in data:
            club_val = data['sport_club_id']
            if isinstance(club_val, int):
                vals['sport_club_id'] = club_val
            elif isinstance(club_val, str):
                club_rec = self.env['sport.club.model'].search([('name', '=', club_val)], limit=1)
                if not club_rec:
                    raise ValidationError(_("Sport club '%s' not found.") % club_val)
                vals['sport_club_id'] = club_rec.id

        if 'sport_id' in data:
            sport_val = data['sport_id']
            if isinstance(sport_val, int):
                vals['sport_id'] = sport_val
            elif isinstance(sport_val, str):
                sport_rec = self.env['sport.club.sports'].search([('name', '=', sport_val)], limit=1)
                if not sport_rec:
                    words = sport_val.strip().split()
                    code = (words[0][0] + (words[-1][0] if len(words) > 1 else words[0][0])).upper()
                    sport_rec = self.env['sport.club.sports'].create({'name': sport_val, 'code': code})
                vals['sport_id'] = sport_rec.id

        return vals

    def _to_api_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "facility_type": self.facility_type,
            "capacity": self.capacity,
            "sport_club_id": self.sport_club_id.id if self.sport_club_id else False,
            "sport_club_name": self.sport_club_id.name if self.sport_club_id else "",
            "sport_id": self.sport_id.id if self.sport_id else False,
            "sport_name": self.sport_id.name if self.sport_id else "",
            "indoor": self.indoor,
            "lighting": self.lighting,
            "surface_type": self.surface_type,
            "color": self.color,
            "active": self.active,
        }
