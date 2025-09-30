from odoo import api,models, fields,_
from odoo.exceptions import ValidationError


class SportClubFacility(models.Model):
    _name = "sport.club.facility"
    _description = "Sport Club Facility"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Facility Name",
        default='New',
        required=True,
        tracking=True,
        copy=False,
        index=True,
        help="Name of the facility (e.g., Court 1, Football Field A)."
    )
    facility_type = fields.Selection(
        selection=[
            ("court", "Court"),
            ("field", "Field"),
            ("room", "Room"),
            ("lane", "Swimming Lane"),
        ],
        string="Facility Type",
        required=True,
        tracking=True,
        help="Type of facility (Court, Field, Room, Swimming Lane)."
    )
    capacity = fields.Integer(
        string="Capacity",
        required=False,
        tracking=True,
        default=1,
        help="Maximum number of players or participants allowed in this facility."
    )
    sport_club_id = fields.Many2one(
        comodel_name="sport.club.model",
        string="Sport Club",
        required=True,
        tracking=True,
        ondelete="cascade",
        index=True,
        help="The sport club that owns this facility."
    )
    sport_id = fields.Many2one(
        comodel_name="sport.club.sports",
        string="Sport",
        required=False,
        tracking=True,
        ondelete="set null",
        index=True,
        help="The sport associated with this facility (if any)."
    )
    calendar_template_id = fields.Many2one(
        comodel_name="sport.club.calendar",
        string="Calendar Template",
        required=False,
        tracking=True,
        help="Defines the default availability schedule for this facility."
    )
    indoor = fields.Boolean(
        string="Indoor",
        default=False,
        tracking=True,
        help="Indicates whether this facility is indoors."
    )
    lighting = fields.Boolean(
        string="Lighting Available",
        default=False,
        tracking=True,
        help="Indicates if the facility has lighting for evening use."
    )
    surface_type = fields.Selection(
        selection=[
            ("grass", "Grass"),
            ("clay", "Clay"),
            ("hard", "Hard"),
        ],
        string="Surface Type",
        required=True,
        tracking=True,
        help="The surface type of the facility (Grass, Clay, Hard)."
    )
    color = fields.Integer(
        string="Color Index",
        required=False,
        tracking=True,
        default=0,
        help="Used to assign a color for this facility in views (e.g., calendar or kanban)."
    )

    @api.constrains("name", "sport_club_id")
    def _check_unique_facility_name_per_club(self):
        """ Ensure facility name is unique per club """
        for rec in self:
            if rec.name and rec.sport_club_id:
                existing = self.search([
                    ("id", "!=", rec.id),
                    ("name", "=", rec.name),
                    ("sport_club_id", "=", rec.sport_club_id.id),
                ], limit=1)
                if existing:
                    raise ValidationError(
                        _("Facility name '%s' already exists in club '%s'.")
                        % (rec.name, rec.sport_club_id.name)
                    )

    @api.constrains("capacity")
    def _check_capacity_positive(self):
        for rec in self:
            if rec.capacity is not None and rec.capacity <= 0:
                raise ValidationError(_("Capacity must be greater than zero."))

    @api.constrains("surface_type", "facility_type")
    def _check_surface_validity(self):
        """Example: Swimming lanes should not have grass/clay/hard surfaces."""
        for rec in self:
            if rec.facility_type == "lane" and rec.surface_type in ["grass", "clay", "hard"]:
                raise ValidationError(
                    _("Swimming lanes cannot have a surface type of %s.") % rec.surface_type
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("sport.club.facility.seq") or _("New")
        return super().create(vals_list)