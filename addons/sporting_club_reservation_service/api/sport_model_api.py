from odoo import api, models, _
from odoo.exceptions import ValidationError, UserError


class SportClubSports(models.Model):
    _inherit = "sport.club.sports"

    @api.model
    def _api_create_sport(self, vals):
        Sport = self.env['sport.club.sports'].sudo()

        if not vals.get('name'):
            raise ValidationError(_("Sport name is required."))

        data = self._from_api_dict(vals)
        sport = Sport.create(data)
        return sport._to_api_dict()

    @api.model
    def _api_search_sports(self, domain=None, limit=100, offset=0):
        Sport = self.env['sport.club.sports'].sudo()
        domain = domain or []
        sports = Sport.search(domain, limit=limit, offset=offset)
        return [s._to_api_dict() for s in sports]

    @api.model
    def _api_get_sport(self, sport_id):
        Sport = self.env['sport.club.sports'].sudo()
        sport = Sport.browse(int(sport_id))
        if not sport.exists():
            raise UserError(_("Sport not found."))
        return sport._to_api_dict()

    @api.model
    def _api_filter_sports_with_keyword(self, keyword):
        if not keyword:
            return []

        Sport = self.env['sport.club.sports'].sudo()
        domain = ['|', ('name', 'ilike', keyword), ('code', 'ilike', keyword)]
        sports = Sport.search(domain)
        return [s._to_api_dict() for s in sports]

    @api.model
    def _api_update_sport(self, vals):
        if 'id' not in vals:
            raise ValidationError(_("Sport ID is required for update."))

        Sport = self.env['sport.club.sports'].sudo()
        sport = Sport.browse(int(vals['id']))
        if not sport.exists():
            raise UserError(_("Sport not found."))

        vals.pop('id', None)
        data = self._from_api_dict(vals)
        sport.write(data)
        return sport._to_api_dict()

    @api.model
    def _api_delete_sport(self, sport_id):
        Sport = self.env['sport.club.sports'].sudo()
        sport = Sport.browse(int(sport_id))
        if not sport.exists():
            raise UserError(_("Sport not found."))

        sport.unlink()
        return {"deleted": True, "id": sport_id}

    @api.model
    def _from_api_dict(self, data):
        vals = {}
        for field in ['name', 'code', 'color', 'active']:
            if field in data:
                vals[field] = data[field]
        return vals

    def _to_api_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code":self.code
        }