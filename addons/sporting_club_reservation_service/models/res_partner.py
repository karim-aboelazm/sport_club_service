# ====================================================================================================
# Odoo Imports Cheat Sheet
# ====================================================================================================

from odoo import models, fields, api, _
import re
# --------------------------------------------------------------------------------
# models -> Base classes to define models/tables
#   - Model          : Persistent model (creates/extends database tables)
#   - TransientModel : Temporary model (data auto-deleted, used in wizards)
#   - AbstractModel  : Abstract class (no table, reusable behaviors)
#
# fields -> Define database columns with datatypes
#   - Char, Text, Integer, Float, Boolean, Date, Datetime
#   - Many2one, One2many, Many2many (relational fields)
#   - Selection, Binary, Html, Monetary, etc.
#
# api -> Decorators and tools for computed/related/constraint logic
#   - @api.model      : Method works on model, not recordset
#   - @api.multi      : Deprecated (use recordsets directly)
#   - @api.depends    : Trigger compute when fields change
#   - @api.onchange   : Trigger UI update when field changes
#   - @api.constrains : Add Python-level validation rules
#   - @api.returns    : Helps specify return type
#
# _ -> Translation helper for multilingual support (wrap translatable strings)
#   Example: raise UserError(_("This record cannot be deleted!"))
# --------------------------------------------------------------------------------

from odoo.exceptions import ValidationError, UserError, AccessError, MissingError, AccessDenied, CacheMiss
# --------------------------------------------------------------------------------
# Common Odoo Exceptions
#   ValidationError -> Raised when user enters invalid data
#   UserError       -> Raised for functional errors (business rules)
#   AccessError     -> Raised when user lacks access rights
#   MissingError    -> Raised when data/record is missing
#   AccessDenied    -> Raised when login/authentication is denied
#   CacheMiss       -> Raised for missing cache data (rare, usually internal)
# --------------------------------------------------------------------------------


class ResPartner(models.Model):
    # --------------------------------------------------------------------------------
    # _inherit -> Extends an existing model
    #   - _name     : Creates a brand-new model/table
    #   - _inherit  : Extends an existing model (adds fields/methods)
    #   - _inherits : Delegates fields from another model (acts like composition)
    #
    # In this case:
    #   class ResPartner(models.Model):
    #       _inherit = 'res.partner'
    #   -> This extends the built-in "res.partner" model (Contacts),
    #      adding custom fields without creating a new database table.
    # --------------------------------------------------------------------------------
    _inherit = 'res.partner'

    # --------------------------------------------------------------------------------
    # Boolean -> True/False value, often used for flags or toggles
    # Example usage here: defining roles for a contact
    # --------------------------------------------------------------------------------
    is_player = fields.Boolean(
        string="Is Player ?",
        default=False,
        help="Check if this contact is a player in the sporting club service."
    )
    is_trainer = fields.Boolean(
        string="Is Trainer ?",
        default=False,
        help="Check if this contact is a trainer in the sporting club service."
    )
    # --------------------------------------------------------------------------------
    # One2many -> One record linked to many related records
    #   - comodel_name : target model
    #   - inverse_name : field on target model pointing back
    # Example: One partner can own multiple sport.club.model records
    # --------------------------------------------------------------------------------
    owned_club_ids = fields.One2many(
        comodel_name="sport.club.model",
        inverse_name="owner_id",
        string='Owned clubs'
    )
    reservation_id = fields.Many2one(
        comodel_name="sport.club.reservation",
        string="Reservation",
    )
    qr_image = fields.Binary(
        string="QR Code",
        attachment=True,
    )

    # @api.constrains("email")
    # def _check_email_format(self):
    #     email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    #     for rec in self:
    #         if rec.email and not re.match(email_regex, rec.email):
    #             raise ValidationError(_("Invalid email format for owner email: %s") % rec.email)

    # @api.constrains("phone", "mobile")
    # def _check_phone_numbers(self):
    #     """Ensure phone numbers follow Egyptian format."""
    #     egypt_mobile_regex = r"^(\+20|0)(10|11|12|15)\d{8}$"
    #     for rec in self:
    #         for number, label in [(rec.phone, "Phone"), (rec.mobile, "Mobile")]:
    #             if number and not re.match(egypt_mobile_regex, number):
    #                 raise ValidationError(_("%s number is invalid for Egypt: %s") % (label, number))