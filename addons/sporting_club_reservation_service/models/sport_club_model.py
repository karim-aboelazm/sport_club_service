from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SportClubModel(models.Model):
    _name = "sport.club.model"
    _inherit = ["mail.activity.mixin", "mail.thread"]
    _description = "Sport Club Model"
    _rec_name = "name"
    _order = "id"

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Name",
        required=True,
        tracking=True
    )
    logo = fields.Binary(
        string="Logo",
        attachment=True,
    )
    description = fields.Text(
        string="Description",
    )
    owner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Owner",
        domain=[('is_club_owner', '=', True)],
        required=True,
        tracking=True
    )
    owner_phone = fields.Char(
        string="Owner Phone",
        related="owner_id.phone"
    )
    owner_mobile = fields.Char(
        string="Owner Mobile",
        related="owner_id.mobile"
    )
    owner_email = fields.Char(
        string="Owner Email",
        related="owner_id.email"
    )
    country_id = fields.Many2one(
        comodel_name="res.country",
        string="Country",
        default=lambda self: self.env.ref("base.eg", raise_if_not_found=False),
        required=True,
        tracking=True
    )
    governorate_id = fields.Many2one(
        comodel_name="res.country.state",
        string="Governorate",
        domain="[('country_id','=?',country_id)]",
        required=True,
        tracking=True
    )
    city_id = fields.Many2one(
        comodel_name="res.country.state.cities",
        string="City",
        domain="[('state_id','=?',governorate_id)]",
        required=True,
        tracking=True
    )
    area_id = fields.Many2one(
        comodel_name="res.country.state.cities.areas",
        string="Area",
        domain="[('city_id','=?',city_id)]",
        tracking=True
    )
    street = fields.Char(
        string="Street",
        required=True,
        tracking=True
    )
    attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        string="Attachments",
        tracking=True
    )
    sport_ids = fields.Many2many(
        comodel_name="sport.club.sports",
        string="Sports Offered",
        tracking=True
    )
    policy_id = fields.Many2one(
        comodel_name="sport.club.policy",
        string="Cancellation Policy",
        tracking=True
    )
    color = fields.Integer(
        string="Color Index",
        required=False,
        tracking=True,
        default=0,
        help="Used to assign a color for this sport in views (e.g., calendar or kanban)."
    )
    facilities_count = fields.Integer(
        string="Facilities Count",
        compute='_calculate_facilities_count'
    )
    calendar_schedual_count = fields.Integer(
        string="Calendar Schedual Count",
        compute='_calculate_calendar_schedual_count'
    )
    pricing_rule_count = fields.Integer(
        string="Pricing Rule Count",
        compute='_calculate_pricing_rule_count'
    )
    promotions_count = fields.Integer(
        string="Promotions Count",
        compute='_calculate_promotions_count'
    )
    reservations_count = fields.Integer(
        string="Reservations Count",
        compute='_calculate_reservations_count'
    )
    trainers_count = fields.Integer(
        string="Trainers Count",
        compute='_calculate_trainers_count'
    )
    trainers_sessions_count = fields.Integer(
        string="Trainers Sessions Count",
        compute='_calculate_trainers_sessions_count'
    )
    def _calculate_facilities_count(self):
        for rec in self:
            rec.facilities_count = self.env['sport.club.facility'].search_count([('sport_club_id','=',rec.id)])

    def _calculate_calendar_schedual_count(self):
        for rec in self:
            club_facilities = self.env['sport.club.facility'].search([('sport_club_id', '=', rec.id)])
            rec.calendar_schedual_count = 0
            if club_facilities:
                rec.calendar_schedual_count = self.env['sport.club.calendar'].search_count([('facility_id','in',club_facilities.ids)])

    def _calculate_pricing_rule_count(self):
        for rec in self:
            rec.pricing_rule_count = self.env['sport.club.pricing.rule'].search_count([('sport_club_id', '=', rec.id)])

    def _calculate_promotions_count(self):
        for rec in self:
            rec.promotions_count = self.env['sport.club.promotion'].search_count([('club_id', '=', rec.id)])

    def _calculate_reservations_count(self):
        for rec in self:
            rec.reservations_count = self.env['sport.club.reservation'].search_count([('club_id', '=', rec.id)])

    def _calculate_trainers_count(self):
        for rec in self:
            rec.trainers_count = self.env['sport.club.trainer'].search_count([('club_id', '=', rec.id)])

    def _calculate_trainers_sessions_count(self):
        for rec in self:
            rec.trainers_sessions_count = self.env['sport.club.training.session'].search_count([('club_id', '=', rec.id)])

    # --------------------------------------
    # VALIDATIONS
    # --------------------------------------
    @api.constrains("name")
    def _check_unique_name(self):
        for rec in self:
            if self.search_count([("name", "=", rec.name), ("id", "!=", rec.id)]):
                raise ValidationError(_("Club name must be unique."))

    @api.constrains("sport_ids")
    def _check_sport_offered(self):
        """Ensure at least one sport is offered."""
        for rec in self:
            if not rec.sport_ids:
                raise ValidationError(_("You must assign at least one sport to the club."))

    @api.constrains("policy_id")
    def _check_policy_validity(self):
        for rec in self:
            if not rec.policy_id:
                raise ValidationError(_("You must assign a cancel policy."))

    # --------------------------------------
    # ONCHANGE HELPERS
    # --------------------------------------
    @api.onchange("country_id")
    def _clear_governorate_if_country_changed(self):
        self.governorate_id = False
        self.city_id = False
        self.area_id = False

    @api.onchange("governorate_id")
    def _clear_city_if_governorate_changed(self):
        self.city_id = False
        self.area_id = False

    @api.onchange("city_id")
    def _clear_area_if_city_changed(self):
        self.area_id = False

        # --- Actions for smart buttons ---

    def action_view_facilities(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Facilities"),
            "res_model": "sport.club.facility",
            "view_mode": "list,form",
            "domain": [("sport_club_id", "=", self.id)],
            "context": {"default_sport_club_id": self.id},
        }

    def action_view_calendar_schedules(self):
        club_facilities = self.env["sport.club.facility"].search([("sport_club_id", "=", self.id)])
        return {
            "type": "ir.actions.act_window",
            "name": _("Calendar Schedules"),
            "res_model": "sport.club.calendar",
            "view_mode": "list,form",
            "domain": [("facility_id", "in", club_facilities.ids)],
            "context": {"default_facility_id": club_facilities[:1].id},
        }

    def action_view_pricing_rules(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Pricing Rules"),
            "res_model": "sport.club.pricing.rule",
            "view_mode": "list,form",
            "domain": [("sport_club_id", "=", self.id)],
            "context": {"default_sport_club_id": self.id},
        }

    def action_view_promotions(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Promotions"),
            "res_model": "sport.club.promotion",
            "view_mode": "list,form",
            "domain": [("club_id", "=", self.id)],
            "context": {"default_club_id": self.id},
        }

    def action_view_reservations(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Reservations"),
            "res_model": "sport.club.reservation",
            "view_mode": "list,form",
            "domain": [("club_id", "=", self.id)],
            "context": {"default_club_id": self.id},
        }

    def action_view_trainers(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Trainers"),
            "res_model": "sport.club.trainer",
            "view_mode": "list,form",
            "domain": [("club_id", "=", self.id)],
            "context": {"default_club_id": self.id},
        }

    def action_view_trainer_sessions(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Trainer Sessions"),
            "res_model": "sport.club.training.session",
            "view_mode": "list,form",
            "domain": [("club_id", "=", self.id)],
            "context": {"default_club_id": self.id},
        }