from odoo import api, fields, models


class SportClubModel(models.Model):
    # --------------------------------------------------------------------------------
    # _name       -> Defines a new model (creates a new database table)
    # _inherit    -> Extends behavior by mixing in features from other models
    # _description-> Human-readable description of the model
    # _rec_name   -> Field used as display name in dropdowns (default is 'name')
    #
    # Here:
    #   - _name="sport.club.model" creates a new table "sport_club_model"
    #   - _inherit=["mail.activity.mixin","mail.thread"]
    #       -> Adds chatter support (followers, activities, messages, tracking)
    #   - _rec_name="name" means the "name" field will be shown in relations
    # --------------------------------------------------------------------------------
    _name = "sport.club.model"
    _inherit = ["mail.activity.mixin", "mail.thread"]
    _description = "Sport Club Model"
    _rec_name = "name"

    # --------------------------------------------------------------------------------
    # Boolean -> True/False value
    #   - Often used for "active/inactive" flags
    # Example: active → controls whether the club is archived or not
    # --------------------------------------------------------------------------------
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # --------------------------------------------------------------------------------
    # Char -> Short text string (single line)
    #   - Used for names, codes, identifiers
    #   - tracking=True means changes are logged in the chatter
    # --------------------------------------------------------------------------------
    name = fields.Char(
        string="Name",
        required=True,
        tracking=True
    )

    # --------------------------------------------------------------------------------
    # Text -> Longer plain text (multi-line)
    #   - Used for descriptions, comments, notes
    # --------------------------------------------------------------------------------
    description = fields.Text(
        string="Description",
    )

    # --------------------------------------------------------------------------------
    # Many2one -> Many records link to ONE record (foreign key)
    #   - comodel_name : target model
    #   - domain       : restrict selectable values
    #   - tracking     : logs changes in chatter
    # Example: owner_id → the partner who owns the club
    # --------------------------------------------------------------------------------
    owner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Owner",
        domain=[('is_club_owner', '=', True)],
        required=True,
        tracking=True
    )

    # --------------------------------------------------------------------------------
    # Many2one (linked to base.country model)
    #   - Default value using env.ref → references XML ID ("base.eg")
    #   - Useful for setting default country
    # --------------------------------------------------------------------------------
    country_id = fields.Many2one(
        comodel_name="res.country",
        string="Country",
        default=lambda self: self.env.ref("base.eg", raise_if_not_found=False),
        required=True,
        tracking=True
    )

    # --------------------------------------------------------------------------------
    # Many2one (linked to res.country.state)
    #   - domain → only states belonging to selected country
    # --------------------------------------------------------------------------------
    governorate_id = fields.Many2one(
        comodel_name="res.country.state",
        string="Governorate",
        domain="[('country_id','=?',country_id)]",
        required=True,
        tracking=True
    )

    # --------------------------------------------------------------------------------
    # Many2one (custom model: res.country.state.cities)
    #   - domain → only cities belonging to selected state
    # --------------------------------------------------------------------------------
    city_id = fields.Many2one(
        comodel_name="res.country.state.cities",
        string="City",
        domain="[('state_id','=?',governorate_id)]",
        required=True,
        tracking=True
    )

    # --------------------------------------------------------------------------------
    # Many2one (custom model: res.country.state.cities.areas)
    #   - domain → only areas belonging to selected city
    # --------------------------------------------------------------------------------
    area_id = fields.Many2one(
        comodel_name="res.country.state.cities.areas",
        string="Area",
        domain="[('city_id','=?',city_id)]",
        required=True,
        tracking=True
    )

    # --------------------------------------------------------------------------------
    # Char -> Street name / address line
    #   - Useful for storing addresses along with country/city hierarchy
    # --------------------------------------------------------------------------------
    street = fields.Char(
        string="Street",
        required=True,
        tracking=True
    )

    # --------------------------------------------------------------------------------
    # Many2many -> Many-to-many relation
    #   - Links multiple records to multiple records
    #   - Example: club can have multiple attachments (files/images)
    # --------------------------------------------------------------------------------
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
    # ============================================================
    # Display Settings
    # ============================================================
    color = fields.Integer(
        string="Color Index",
        required=False,
        tracking=True,
        default=0,
        help="Used to assign a color for this sport in views (e.g., calendar or kanban)."
    )