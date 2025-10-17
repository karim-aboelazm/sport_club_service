# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError, UserError


class SportClubPolicy(models.Model):
    _inherit = "sport.club.policy"

    @api.model
    def _api_create_policy(self, vals):
        if not vals.get('name'):
            raise ValidationError(_("Policy name is required."))

        data = self._from_api_dict(vals)
        policy = self.sudo().create(data)
        return policy._to_api_dict()

    @api.model
    def _api_search_policies(self, domain=None, limit=100, offset=0):
        domain = domain or []
        policies = self.search(domain, limit=limit, offset=offset)
        return [policy._to_api_dict() for policy in policies]

    @api.model
    def _api_get_policy(self, policy_id):
        policy = self.browse(int(policy_id))
        if not policy.exists():
            raise UserError(_("Policy not found."))
        return policy._to_api_dict()

    @api.model
    def _api_filter_policies_with_keyword(self, keyword):
        if not keyword:
            return []

        conditions = [
            ('name', 'ilike', keyword),
            ('club_id.name', 'ilike', keyword),
            ('state', 'ilike', keyword),
        ]
        domain = ['|'] * (len(conditions) - 1) + conditions
        policies = self.search(domain)
        return [policy._to_api_dict() for policy in policies]

    def _api_update_policy(self, vals):
        if 'id' not in vals:
            raise ValidationError(_("Policy ID is required for update."))

        policy = self.browse(int(vals['id']))
        if not policy.exists():
            raise UserError(_("Policy not found."))

        vals.pop('id', None)
        data = self._from_api_dict(vals)
        policy.sudo().write(data)
        return policy._to_api_dict()

    @api.model
    def _api_delete_policy(self, policy_id):
        policy = self.browse(int(policy_id))
        if not policy.exists():
            raise UserError(_("Policy not found."))

        policy.unlink()
        return {"deleted": True, "id": policy_id}

    @api.model
    def _from_api_dict(self, data):
        vals = {}

        simple_fields = [
            'name',
            'active',
            'state',
            'free_cancel_before_hours',
            'refund_percent_before_hours',
            'no_show_penalty_percent',
            'reschedule_allowed',
            'color',
        ]
        for field in simple_fields:
            if field in data:
                vals[field] = data[field]

        if 'club_id' in data:
            club_val = data['club_id']
            if isinstance(club_val, int):
                vals['club_id'] = club_val
            elif isinstance(club_val, str):
                club = self.env['sport.club.model'].search([('name', '=', club_val)], limit=1)
                if club:
                    vals['club_id'] = club.id

        return vals

    def _to_api_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "active": self.active,
            "state": self.state,
            "club_id": self.club_id.id if self.club_id else False,
            "club_name": self.club_id.name if self.club_id else "",
            "free_cancel_before_hours": self.free_cancel_before_hours,
            "refund_percent_before_hours": self.refund_percent_before_hours,
            "no_show_penalty_percent": self.no_show_penalty_percent,
            "reschedule_allowed": self.reschedule_allowed,
            "color": self.color,
            "usage_reservation_count": self.usage_reservation_count,
        }
