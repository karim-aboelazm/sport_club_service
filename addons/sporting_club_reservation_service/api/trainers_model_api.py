# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, UserError
from bs4 import BeautifulSoup
import html


def _convert_bio(data, to_html=False):
    if not data:
        return ""

    if to_html:
        escaped_text = html.escape(data)
        paragraphs = [f"<p>{p.strip().replace('\n', '<br>')}</p>" for p in escaped_text.split('\n\n') if p.strip()]
        return "\n".join(paragraphs)
    else:
        soup = BeautifulSoup(data, "html.parser")
        return soup.get_text(separator="\n", strip=True)

class SportClubTrainer(models.Model):
    _inherit = "sport.club.trainer"

    @api.model
    def _api_create_trainer(self, vals):
        Trainer = self.env['sport.club.trainer'].sudo()

        if not vals.get('name'):
            raise ValidationError(_("Trainer (name) is required."))

        data = self._from_api_dict(vals)
        trainer = Trainer.create(data)
        return trainer._to_api_dict()

    @api.model
    def _api_search_trainers(self, domain=None, limit=100, offset=0):
        Trainer = self.env['sport.club.trainer'].sudo()
        domain = domain or []
        trainers = Trainer.search(domain, limit=limit, offset=offset)
        return [t._to_api_dict() for t in trainers]

    @api.model
    def _api_get_trainer(self, trainer_id):
        Trainer = self.env['sport.club.trainer'].sudo()
        trainer = Trainer.browse(int(trainer_id))
        if not trainer.exists():
            raise UserError(_("Trainer not found."))
        return trainer._to_api_dict()

    @api.model
    def _api_filter_trainers_with_keyword(self, keyword):
        if not keyword:
            return []

        Trainer = self.env['sport.club.trainer'].sudo()
        domain = [
            '|', '|', '|', '|', '|',
            ('partner_id.name', 'ilike', keyword),
            ('club_id.name', 'ilike', keyword),
            ('sport_ids.name', 'ilike', keyword),
            ('calendar_template_id.name', 'ilike', keyword),
            ('priority', 'ilike', keyword),
            ('bio', 'ilike', keyword),
        ]
        try:
            rate = float(keyword)
            domain.insert(0,'|')
            domain.append(('hourly_rate', '=', rate))
        except:
            pass
        trainers = Trainer.search(domain)
        return [t._to_api_dict() for t in trainers]

    @api.model
    def _api_update_trainer(self, vals):
        if 'id' not in vals:
            raise ValidationError(_("Trainer ID is required for update."))

        Trainer = self.env['sport.club.trainer'].sudo()
        trainer = Trainer.browse(int(vals['id']))
        if not trainer.exists():
            raise UserError(_("Trainer not found."))

        vals.pop('id', None)
        data = self._from_api_dict(vals)
        trainer.write(data)
        return trainer._to_api_dict()

    @api.model
    def _api_delete_trainer(self, trainer_id):
        Trainer = self.env['sport.club.trainer'].sudo()
        trainer = Trainer.browse(int(trainer_id))
        if not trainer.exists():
            raise UserError(_("Trainer not found."))

        trainer.unlink()
        return {"deleted": True, "id": trainer_id}

    @api.model
    def _from_api_dict(self, data):
        vals = {}

        for field in ['active', 'priority', 'hourly_rate']:
            if field in data:
                vals[field] = data[field]

        if 'bio' in data and data['bio']:
            vals['bio'] = _convert_bio(data['bio'],to_html=True)

        # Partner
        if 'name' in data and data['name']:
            partner_val = data['name']
            partner_model = self.env['res.partner'].sudo()

            if isinstance(partner_val, str):
                partner = partner_model.search([('name', '=', partner_val), ('is_trainer', '=', True)], limit=1)
                if not partner:
                    partner = partner_model.create({
                        'name': partner_val,
                        'company_id':self.env.company.id,
                        'is_trainer': True,
                        'type': 'contact',
                    })
                vals['partner_id'] = partner.id

        # Club
        if 'club_id' in data and data['club_id']:
            club_val = data['club_id']
            club_model = self.env['sport.club.model'].sudo()
            if isinstance(club_val, int):
                vals['club_id'] = club_val
            elif isinstance(club_val, str):
                club = club_model.search([('name', '=', club_val)], limit=1)
                if not club:
                    raise ValidationError(_("Club with name '%s' not found.") % club_val)
                vals['club_id'] = club.id

        # calendar
        if 'calendar_template_id' in data and data['calendar_template_id']:
            calendar_val = data['calendar_template_id']
            calendar_model = self.env['sport.club.calendar'].sudo()
            if isinstance(calendar_val, int):
                vals['calendar_template_id'] = calendar_val
            elif isinstance(calendar_val, str):
                calendar = calendar_model.search([('name','=',calendar_val)],limit=1)
                if not calendar:
                    raise ValidationError(_("Calendar with name '%s' not found. ") % calendar_val)
                vals['calendar_template_id'] = calendar.id

        # Sports (many2many)
        if 'sport_ids' in data and data['sport_ids']:
            sport_model = self.env['sport.club.sports'].sudo()
            sport_ids = []
            for sport_val in data['sport_ids']:
                if isinstance(sport_val, int):
                    sport_ids.append(sport_val)
                elif isinstance(sport_val, str):
                    sport = sport_model.search([('name', '=', sport_val)], limit=1)
                    if not sport:
                        raise ValidationError(_("Sport with name '%s' not found.") % sport_val)
                    sport_ids.append(sport.id)
            vals['sport_ids'] = [(6, 0, sport_ids)]

        return vals

    def _to_api_dict(self):
        self.ensure_one()
        return {
            "id": self.id,
            "name": self.partner_id.display_name if self.partner_id else "",
            "club": {
                "id": self.club_id.id if self.club_id else False,
                "name": self.club_id.display_name if self.club_id else "",
            },
            "sports": [
                {"id": s.id, "name": s.display_name} for s in self.sport_ids
            ],
            "calendar_template": {
                "id": self.calendar_template_id.id if self.calendar_template_id else False,
                "name": self.calendar_template_id.display_name if self.calendar_template_id else "",
            },
            "hourly_rate": self.hourly_rate,
            "currency": {
                "id": self.currency_id.id if self.currency_id else False,
                "name": self.currency_id.name if self.currency_id else False,
                "symbol": self.currency_id.symbol if self.currency_id else False,
            },
            "priority": self.priority,
            "bio": _convert_bio(self.bio).replace('\n',' ') or "",
            "active": self.active,
            "session_count": self.session_count,
        }