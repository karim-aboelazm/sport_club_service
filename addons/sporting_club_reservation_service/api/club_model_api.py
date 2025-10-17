from odoo import api, models, _
from odoo.exceptions import ValidationError, UserError

class SportClubModel(models.Model):
    _inherit = "sport.club.model"

    @api.model
    def _api_create_club(self, vals):
        """
        Create a new sport club via API.
        :param vals: dict of fields
        :return: dict (created record data)
        """
        if not vals.get('name'):
            raise ValidationError(_("Name is required."))
        data = self._from_api_dict(vals)
        club = self.sudo().create(data)
        return club._to_api_dict()

    @api.model
    def _api_search_clubs(self, domain=None, limit=100, offset=0):
        """
        Search sport clubs based on domain.
        :param domain: list of tuples [('field', '=', value)]
        :param limit: int
        :param offset: int
        :return: list of dicts
        """
        domain = domain or []
        clubs = self.search(domain, limit=limit, offset=offset)
        return [club._to_api_dict() for club in clubs]

    @api.model
    def _api_get_club(self, club_id):
        """
        Get single club by ID.
        """
        club = self.browse(int(club_id))
        if not club.exists():
            raise UserError(_("Sport club not found."))
        return club._to_api_dict()

    @api.model
    def _filter_clubs_with_keywords(self, keyword):
            """
            Search clubs by keyword in multiple related fields.
            Return serialized dicts using _to_api_dict().
            """
            if not keyword:
                return []

            conditions = [
                ('name', 'ilike', keyword),
                ('description', 'ilike', keyword),
                ('owner_id.name', 'ilike', keyword),
                ('city_id.name_en', 'ilike', keyword),
                ('city_id.name_ar', 'ilike', keyword),
                ('area_id.name', 'ilike', keyword),
                ('street', 'ilike', keyword),
                ('sport_ids.name', 'ilike', keyword),
                ('governorate_id.name', 'ilike', keyword),
                ('country_id.name', 'ilike', keyword),
                ('owner_id.phone', 'ilike', keyword),
                ('owner_id.mobile', 'ilike', keyword),
                ('owner_id.email', 'ilike', keyword),
            ]

            domain = ['|'] * (len(conditions) - 1) + conditions

            clubs = self.search(domain)
            return [club._to_api_dict() for club in clubs]

    def _api_update_club(self, vals):
        """
        Update existing club via API.
        :param vals: dict with at least 'id'
        """
        if 'id' not in vals:
            raise ValidationError(_("Club ID is required for update."))

        club = self.browse(int(vals['id']))
        if not club.exists():
            raise UserError(_("Sport club not found."))

        vals.pop('id', None)
        data = self._from_api_dict(vals)
        club.sudo().write(data)
        return club._to_api_dict()

    @api.model
    def _api_delete_club(self, club_id):
        """
        Delete a club by ID.
        """
        club = self.browse(int(club_id))
        if not club.exists():
            raise UserError(_("Sport club not found."))

        club.unlink()
        return {"deleted": True, "id": club_id}

    @api.model
    def _from_api_dict(self, data):
        vals = {}

        # --- Simple Fields ---
        simple_fields = ['name', 'description', 'street', 'color', 'active', 'logo']
        for field in simple_fields:
            if field in data:
                vals[field] = data[field]

        # --- Owner ---
        if 'owner_id' in data:
            owner_val = data['owner_id']
            if isinstance(owner_val, int):
                vals['owner_id'] = owner_val
            elif isinstance(owner_val, str):
                owner_rec = self.env['res.users'].search([('name', '=', owner_val)], limit=1)
                if owner_rec:
                    vals['owner_id'] = owner_rec.id

        # --- Country ---
        if 'country_id' in data:
            country_val = data['country_id']
            if isinstance(country_val, int):
                vals['country_id'] = country_val
            elif isinstance(country_val, str):
                country_rec = self.env['res.country'].search([('name', '=', country_val)], limit=1)
                if not country_rec:
                    country_rec = self.env['res.country'].create({'name': country_val})
                vals['country_id'] = country_rec.id

        # --- Governorate ---
        governorate_id = False
        if 'governorate_id' in data:
            gov_val = data['governorate_id']
            if isinstance(gov_val, int):
                governorate_id = gov_val
            elif isinstance(gov_val, str):
                gov_rec = self.env['res.country.state'].search([('name', '=', gov_val)], limit=1)
                if not gov_rec:
                    gov_rec = self.env['res.country.state'].create({
                        'name': gov_val,
                        'country_id': vals.get('country_id')
                    })
                governorate_id = gov_rec.id
            vals['governorate_id'] = governorate_id

        # --- City ---
        city_id = False
        if 'city_id' in data:
            city_val = data['city_id']
            if isinstance(city_val, int):
                city_id = city_val
            elif isinstance(city_val, str):
                domain = [('name_en', '=', city_val)]
                if governorate_id:
                    domain.append(('state_id', '=', governorate_id))
                city_rec = self.env['res.country.state.cities'].search(domain, limit=1)
                if not city_rec:
                    city_rec = self.env['res.country.state.cities'].create({
                        'name_en': city_val,
                        'name_ar': city_val,
                        'state_id': governorate_id,
                    })
                city_id = city_rec.id
            vals['city_id'] = city_id

        # --- Area ---
        if 'area_id' in data:
            area_val = data['area_id']
            if isinstance(area_val, int):
                vals['area_id'] = area_val
            elif isinstance(area_val, str):
                domain = [('name', '=', area_val)]
                if governorate_id:
                    domain.append(('state_id', '=', governorate_id))
                if city_id:
                    domain.append(('city_id', '=', city_id))
                area_rec = self.env['res.country.state.cities.areas'].search(domain, limit=1)
                if not area_rec:
                    area_rec = self.env['res.country.state.cities.areas'].create({
                        'name': area_val,
                        'state_id': governorate_id,
                        'city_id': city_id,
                    })
                vals['area_id'] = area_rec.id

        # --- Many2many: Sports with Code ---
        if 'sport_ids' in data:
            sport_ids = []
            for item in data['sport_ids']:
                sport_name = item if isinstance(item, str) else item.get('name')
                if not sport_name:
                    continue

                # Generate code: first letter of first word + first letter of last word
                words = sport_name.strip().split()
                first_letter = words[0][0].upper() if words else ''
                last_letter = words[-1][0].upper() if len(words) > 0 else ''
                sport_code = f"{first_letter}{last_letter}"

                sport_rec = self.env['sport.club.sports'].search([('name', '=', sport_name)], limit=1)
                if not sport_rec:
                    sport_rec = self.env['sport.club.sports'].create({
                        'name': sport_name,
                        'code': sport_code
                    })
                sport_ids.append(sport_rec.id)
            vals['sport_ids'] = [(6, 0, sport_ids)]

        # --- Many2many: Attachments ---
        if 'attachment_ids' in data:
            attach_ids = []
            for item in data['attachment_ids']:
                attach_name = item if isinstance(item, str) else item.get('name')
                if not attach_name:
                    continue
                attach_rec = self.env['ir.attachment'].search([('name', '=', attach_name)], limit=1)
                if not attach_rec:
                    attach_rec = self.env['ir.attachment'].create({'name': attach_name})
                attach_ids.append(attach_rec.id)
            vals['attachment_ids'] = [(6, 0, attach_ids)]

        return vals

    def _to_api_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description or "",
            "owner_id": self.owner_id.id if self.owner_id else False,
            "owner_name": self.owner_id.name if self.owner_id else "",
            "owner_phone": self.owner_phone if self.owner_phone else "",
            "owner_mobile": self.owner_mobile if self.owner_mobile else "",
            "owner_email": self.owner_email if self.owner_email else "",
            "country_id": self.country_id.id if self.country_id else False,
            "country_name": self.country_id.name if self.country_id else "",
            "governorate_id": self.governorate_id.id if self.governorate_id else False,
            "city_id": self.city_id.id if self.city_id else False,
            "street": self.street,
            "active": self.active,
        }
