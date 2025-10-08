import io
import random
import string
import base64
import qrcode
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError


class Reservation(models.Model):
    _name = "sport.club.reservation"
    _description = "Reservation"
    _inherit = ["mail.thread", "mail.activity.mixin"]


    # ============================================================
    # Basic Information
    # ============================================================
    active = fields.Boolean(
        string="Active",
        default=True
    )
    name = fields.Char(
        string="Reservation Name",
        default='New',
        copy=False,
        required=True,
        readonly=True,
        tracking=True,
    )
    code = fields.Char(
        string="Reservation Code",
        default="New",
        copy=False,
        index=True,
        tracking=True,
        help="Unique code for reservation identification.",
    )

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("requested", "Requested"),
            ("confirmed", "Confirmed"),
            ("checked_in", "Checked In"),
            ("checked_out", "Checked Out"),
            ("cancelled", "Cancelled"),
            ("refunded", "Refunded"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    source = fields.Selection(
        selection=[
            ("backend", "Backend"),
            ("portal", "Portal"),
            ("app", "App")
        ],
        string="Booking Source",
        default="backend",
        tracking=True,
    )

    # ============================================================
    # Player & Club
    # ============================================================
    player_id = fields.Many2one(
        comodel_name="res.partner",
        string="Player",
        domain=[("is_player", "=", True)],
        tracking=True,
    )
    club_id = fields.Many2one(
        comodel_name="sport.club.model",
        string="Club",
        required=True,
        tracking=True,
    )
    facility_id = fields.Many2one(
        comodel_name="sport.club.facility",
        string="Facility",
        required=True,
        tracking=True,
    )
    sport_ids = fields.Many2many(
        comodel_name="sport.club.sports",
        string="Sports Offered",
        related="club_id.sport_ids",
    )
    sport_id = fields.Many2one(
        comodel_name="sport.club.sports",
        domain=lambda self:[('id','in',self.club_id.sport_ids.ids)],
        string="Sport",
        tracking=True,
    )

    # ============================================================
    # Scheduling
    # ============================================================
    date = fields.Date(
        string="Date",
        default=fields.Date.today(),
        tracking=True
    )
    time_from = fields.Float(
        string="From Time",
        required=True,
        tracking=True,
    )
    time_to = fields.Float(
        string="To Time",
        required=True,
        tracking=True,
    )
    duration_hours = fields.Float(
        string="Duration",
        compute="_compute_duration",
        store=True,
        help="Automatically calculated as End - Start in hours.",
    )

    # ============================================================
    # Financials
    # ============================================================
    pricing_rule_id = fields.Many2one(
        comodel_name='sport.club.pricing.rule',
        string="Pricing Rule",
        tracking=True,
    )
    price_hour = fields.Monetary(
        string="Hourly Price",
        related='pricing_rule_id.base_price',
        tracking=True,
    )
    price_subtotal = fields.Monetary(
        string="Subtotal",
        compute="_compute_subtotal",
        store=True,
        tracking=True,
        help="Automatically calculated: duration_hours × price_hour",
    )
    amount_equipment = fields.Monetary(
        string="Equipment Total",
        compute="_compute_amount_equipment",
    )
    amount_trainer = fields.Monetary(
        string="Trainer Fee",
        related="trainer_id.hourly_rate",
    )
    promotion_id = fields.Many2one(
        comodel_name="sport.club.promotion",
        string="Promotion Applied",
    )
    tax_id = fields.Many2one(
        comodel_name="account.tax",
        string="Taxes",
        related='pricing_rule_id.tax_id',
        tracking=True,
    )
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        compute="_compute_totals",
        store=True,
        tracking=True,
    )
    amount_tax = fields.Monetary(
        string="Taxes",
        compute="_compute_totals",
        store=True,
        tracking=True,
    )
    amount_total = fields.Monetary(
        string="Total Amount",
        compute="_compute_totals",
        store=True,
        tracking=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        required=True,
        tracking=True,
        default=lambda self: self.env.company.currency_id,
    )
    payment_state = fields.Selection(
        selection=[
            ("unpaid", "Unpaid"),
            ("partial", "Partially Paid"),
            ("paid", "Paid"),
            ("refunded", "Refunded"),
        ],
        compute='_compute_payment_state',
        string="Payment Status",
        default="unpaid",
    )
    payment_ids = fields.Many2many(
        comodel_name="account.payment",
        compute='_get_all_payments',
        string="Payments"
    )

    # ============================================================
    # QR / Tracking
    # ============================================================
    qr_image = fields.Binary(
        string="QR Code",
        attachment=True,
    )
    notes = fields.Text(
        string="Notes",
        tracking=True
    )

    # ============================================================
    # Relations
    # ============================================================
    equipment_line_ids = fields.One2many(
        comodel_name="sport.club.equipment.booking",
        inverse_name="reservation_id",
        string="Equipment Bookings",
    )
    trainer_id = fields.Many2one(
        comodel_name="sport.club.trainer",
        string="Trainer",
        tracking=True
    )
    policy_id = fields.Many2one(
        comodel_name="sport.club.policy",
        string="Cancellation Policy",
        tracking=True
    )

    # ============================================================
    # Check-in/out
    # ============================================================
    checkin_at = fields.Datetime(
        string="Check-in At",
        tracking=True
    )
    checkout_at = fields.Datetime(
        string="Check-out At",
        tracking=True
    )

    # ============================================================
    # Multi-company
    # ============================================================
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self:self.env.company.id,
        tracking=True
    )

    number_of_attandance = fields.Integer(
        string="Number Of Attendance",
        default=1,
        tracking=True,
    )

    color = fields.Integer(
        string="Color Index",
        required=False,
        tracking=True,
        default=0,
        help="Used to assign a color for this facility in views (e.g., calendar or kanban)."
    )

    partner_include_attendance = fields.Boolean(
        string='Partner Include Attendance',
        required=False,
        tracking=True,
    )
    attendance_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="reservation_id",
        string='Reservation Attendance'
    )
    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        copy=False
    )
    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice",
        copy=False
    )
    payment_count = fields.Integer(
        compute='_compute_payment_count'
    )
    invoice_full_paid = fields.Boolean(
        compute='_check_invoice_is_full_paid'
    )
    training_session_count = fields.Integer(
        string="Training Sessions",
        compute="_compute_training_session_count",
    )

    # ============================================================
    # Compute Methods
    # ============================================================

    def _compute_training_session_count(self):
        TrainingSession = self.env['sport.club.training.session']
        for rec in self:
            rec.training_session_count = TrainingSession.search_count([('reservation_id', '=', rec.id)])

    @api.depends('invoice_id')
    def _compute_payment_count(self):
        for rec in self:
            move_ids = []
            if rec.invoice_id:
                move_ids.append(rec.invoice_id.id)

                # Include credit notes (refunds) linked to this invoice
                credit_notes = self.env['account.move'].search([
                    ('reversed_entry_id', '=', rec.invoice_id.id),
                    ('move_type', '=', 'out_refund'),
                ])
                move_ids += credit_notes.ids

            if move_ids:
                rec.payment_count = self.env['account.payment'].search_count([
                    ('invoice_ids', 'in', move_ids)
                ])
            else:
                rec.payment_count = 0

    @api.depends('invoice_id')
    def _check_invoice_is_full_paid(self):
        for rec in self:
            rec.invoice_full_paid = rec.invoice_id.amount_residual == 0.0

    @api.depends('invoice_id')
    def _get_all_payments(self):
        for rec in self:
            move_ids = [self.invoice_id.id]

            # Add credit note(s) created from refund
            credit_notes = self.env['account.move'].search([
                ('reversed_entry_id', '=', self.invoice_id.id),
                ('move_type', '=', 'out_refund'),
            ])
            move_ids += credit_notes.ids
            all_payments = self.env['account.payment'].search([('invoice_ids','in',move_ids)])
            rec.payment_ids = [(6,0,all_payments.ids)]

    @api.depends('invoice_id', 'invoice_id.payment_state')
    def _compute_payment_state(self):
        for rec in self:
            if rec.invoice_id:
                if rec.invoice_id.payment_state == 'paid':
                    rec.payment_state = 'paid'
                elif rec.invoice_id.payment_state == 'partial':
                    rec.payment_state = 'partial'
                elif rec.invoice_id.payment_state == 'reversed':
                    rec.payment_state = 'refunded'
                else:
                    rec.payment_state = 'unpaid'
            else:
                rec.payment_state = 'unpaid'

    @api.depends("time_from", "time_to")
    def _compute_duration(self):
        for rec in self:
            if rec.time_from and rec.time_to:
                delta = rec.time_to - rec.time_from
                rec.duration_hours = delta
            else:
                rec.duration_hours = 0.0

    @api.depends("duration_hours", "price_hour")
    def _compute_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.duration_hours * rec.price_hour if rec.duration_hours and rec.price_hour else 0.0

    @api.depends("price_subtotal", "amount_equipment", "amount_trainer", "tax_id")
    def _compute_totals(self):
        for rec in self:
            base = rec.price_subtotal + rec.amount_equipment + rec.amount_trainer
            taxes_res = rec.tax_id.compute_all(base, rec.currency_id) if rec.tax_id else {"taxes": [], "total_included": base, "total_excluded": base}
            rec.amount_untaxed = taxes_res["total_excluded"]
            rec.amount_tax = sum(t.get("amount", 0.0) for t in taxes_res["taxes"])
            rec.amount_total = taxes_res["total_included"]

    @api.depends("equipment_line_ids")
    def _compute_amount_equipment(self):
        for rec in self:
            rec.amount_equipment = sum(rec.equipment_line_ids.mapped('price_subtotal'))
            rec._compute_subtotal()
            rec._compute_totals()

    @api.constrains('attendance_ids', 'number_of_attandance', 'partner_include_attendance')
    def _check_adding_attendees(self):
        for rec in self:
            allowed = 0
            if rec.number_of_attandance > 1:
                allowed = rec.number_of_attandance if not rec.partner_include_attendance else rec.number_of_attandance - 1

            if rec.attendance_ids and len(rec.attendance_ids) > allowed:
                raise ValidationError(
                    f"You cannot add more than {allowed} attendees for this reservation.\n"
                    f"Currently added: {len(rec.attendance_ids)}"
                )

    @api.constrains('promotion_id', 'amount_total')
    def _check_promotion_id(self):
        for rec in self:
            promotion = rec.promotion_id
            if promotion:
                if promotion.discount_type == 'fixed':
                    if promotion.discount_value >= rec.amount_total:
                        raise ValidationError(_(
                            "The fixed discount (%s) for promotion '%s' cannot be greater than or equal to the total amount (%s)."
                        ) % (promotion.discount_value, promotion.name, rec.amount_total))

    @api.constrains('date', 'time_from', 'time_to', 'facility_id', 'sport_id')
    def _check_reservation_availablaty(self):
        for rec in self:
            if not rec.facility_id or not rec.date:
                continue

            if rec.time_from >= rec.time_to:
                raise ValidationError(_("The 'From Time' must be earlier than the 'To Time'."))

            overlapping_reservations = self.search([
                ('id', '!=', rec.id),
                ('facility_id', '=', rec.facility_id.id),
                ('sport_id', '=', rec.sport_id.id),
                ('date', '=', rec.date),
                ('state', 'in', ['requested', 'confirmed','checked_in']),
                '|',
                '&', ('time_from', '<', rec.time_to), ('time_to', '>', rec.time_from),
                '&', ('time_from', '<', rec.time_from), ('time_to', '>', rec.time_from),
            ], limit=1)

            if overlapping_reservations:
                raise ValidationError(_(
                    "The selected time slot overlaps with an existing reservation "
                    "for the same facility and sport on %s between %.2f and %.2f."
                ) % (rec.date, overlapping_reservations.time_from, overlapping_reservations.time_to))

    def _generate_reservation_code(self):
        length = 5
        characters = string.ascii_uppercase + string.digits
        characters = ''.join(c for c in characters if c not in '01IO')

        while True:
            code = "-".join(
                ''.join(random.choice(characters) for _ in range(length))
                for _ in range(3)
            )
            if not self.search([('code', '=', code)]):
                return code

    def _remove_all_attendees_after_checking_out(self):
        for rec in self:
            if rec.attendance_ids:
                rec.sudo().attendance_ids.unlink()

    def _prepare_qr_content(self, att):
        text = ""
        for rec in self:
            text = (
                f"Reservation Confirmation\n"
                f"---------------------------\n"
                f"Attendee : {att.name}\n"
                f"Code     : {rec.code}\n"
                f"Club     : {rec.club_id.name or ''}\n"
                f"Facility : {rec.facility_id.name or ''}\n"
                f"Sport    : {rec.sport_id.name or ''}\n"
                f"Date     : {rec.date or ''}\n"
                f"Time     : {rec.time_from} - {rec.time_to}\n"
                f"Amount   : {rec.amount_total} {rec.currency_id.symbol or ''}\n"
                f"Payment  : {dict(rec._fields['payment_state'].selection).get(rec.payment_state, '')}\n"
                f"Status   : {dict(rec._fields['state'].selection).get(rec.state, '')}\n"
                f"---------------------------\n"
                f"Thank you for booking with us!"
            )
        return text

    def _create_attendance_qr_code(self):
        for rec in self:
            for att in rec.attendance_ids:
                txt = rec._prepare_qr_content(att)
                qr = qrcode.make(txt)
                buffer = io.BytesIO()
                qr.save(buffer, format='PNG')
                qr_bytes = buffer.getvalue()
                qr_base64 = base64.b64encode(qr_bytes).decode('utf-8')
                att.qr_image = qr_base64

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sport.club.reservation.seq')

            if vals.get('code', 'New') == 'New':
                vals['code'] = self._generate_reservation_code()
        return super().create(vals_list)

    def generate_qr_code(self):
        for record in self:
            if not record.code:
                record.qr_image = False
                continue
            if not record.attendance_ids or record.state != 'confirmed':
                continue
            record._create_attendance_qr_code()

    def action_refund(self):
        """Refund the reservation by creating and reconciling a credit note for the invoice."""
        for rec in self:
            # Ensure there is an invoice
            if not rec.invoice_id:
                raise UserError(_("No invoice found to refund."))

            # Invoice must be posted before we can refund
            if rec.invoice_id.state != 'posted':
                raise UserError(_("You can only refund a posted invoice."))

            # Create reversal wizard to generate credit note
            reversal_wizard = self.env['account.move.reversal'].with_context(
                active_model='account.move',
                active_ids=rec.invoice_id.ids
            ).create({
                'reason': _('Reservation Refund'),
                'journal_id': rec.invoice_id.journal_id.id,
                'date': fields.Date.today(),
            })

            # Trigger the reversal (this creates the credit note)
            reversal_wizard.reverse_moves()

            # Find the created credit note
            credit_note = self.env['account.move'].search([
                ('reversed_entry_id', '=', rec.invoice_id.id),
                ('move_type', '=', 'out_refund'),
            ], limit=1)

            if not credit_note:
                raise UserError(_("Refund failed: Credit note not created."))

            # Post the credit note if not already
            if credit_note.state != 'posted':
                credit_note.action_post()

            # Reconcile invoice & credit note (customer receivable lines)
            receivable_lines = (rec.invoice_id.line_ids + credit_note.line_ids).filtered(
                lambda line: line.account_id.internal_group == 'asset' and not line.reconciled
            )
            if receivable_lines:
                receivable_lines.reconcile()

            # Update reservation state to refunded
            rec.write({'state': 'refunded'})

    def _find_or_create_traniner_fees_product(self):
        product_model = self.env['product.product']
        domain = [('default_code','=','trainer_00_trainer'),('type','=','service'),('name','ilike','Traner Fees')]
        product = product_model.sudo().search(domain,limit=1)
        if not product:
            values = {
                'name':'Traner Fees',
                'default_code':'trainer_00_trainer',
                'type':'service',
                'sale_ok':True,
                'description_sale':'Generic Trainer Fees On reservation service'
            }
            product = product_model.sudo().create(values)
        return product

    def _find_or_create_reservation_product(self):
        product_model = self.env['product.product']
        domain = [('default_code','=','club_00_club'),('type','=','service'),('name','ilike','Club Reservation')]
        product = product_model.sudo().search(domain,limit=1)
        if not product:
            values = {
                'name':'Club Reservation',
                'default_code':'club_00_club',
                'type':'service',
                'sale_ok':True,
                'description_sale':'Generic club reservation service'
            }
            product = product_model.sudo().create(values)
        return product

    def _find_or_create_promotion_product(self):
        product_model = self.env['product.product']
        domain = [('default_code','=','promotion_00_promotion'),('type','=','service'),('name','ilike',self.promotion_id.name)]
        product = product_model.sudo().search(domain,limit=1)
        if not product:
            values = {
                'name':self.promotion_id.name,
                'default_code':'promotion_00_promotion',
                'type':'service',
                'sale_ok':True,
                'description_sale':'Generic Promotion Discount'
            }
            product = product_model.sudo().create(values)
        return product

    def _prepare_dicount_proccess(self):
        for rec in self:
            if rec.promotion_id and rec.promotion_id.discount_type == 'fixed':
                promotion_product_id = rec._find_or_create_promotion_product()
                return [(0, 0, {
                    "product_id": promotion_product_id.id,
                    "name": promotion_product_id.description_sale or "Promotions",
                    "product_uom_qty": 1.0,
                    "price_unit": -1 * self.promotion_id.discount_value,
                    "tax_id": [(6, 0, [])],
                })]
            elif rec.promotion_id and rec.promotion_id.discount_type == 'percent':
                return self.promotion_id.discount_value
        return None

    def _prepare_sale_order_lines(self):
        reservation_product = self._find_or_create_reservation_product()
        trainer_product = self._find_or_create_traniner_fees_product()
        promotion_value = self._prepare_dicount_proccess()
        disc = promotion_value if promotion_value and isinstance(promotion_value,float) else 0.0
        all_products_data = [
            (0, 0, {
                "product_id": reservation_product.id,
                "name": reservation_product.description_sale or "Reservation Service",
                "product_uom_qty": self.duration_hours or 1.0,
                "price_unit": self.price_hour,
                "discount":disc,
                "tax_id": [(6, 0, self.tax_id.ids)],
            }),
            (0, 0, {
                "product_id": trainer_product.id,
                "name": trainer_product.description_sale or "Trainer Fee",
                "product_uom_qty": 1.0,
                "discount":disc,
                "price_unit": self.amount_trainer,
                "tax_id": [(6, 0, self.tax_id.ids)],
            }),
        ]

        # Add equipment lines
        for line in self.equipment_line_ids:
            if line.equipment_product_id:
                all_products_data.append(
                    (0, 0, {
                        "product_id": line.equipment_product_id.id,
                        "name": line.name,
                        "product_uom_qty": line.qty,
                        "discount":disc,
                        "price_unit": (line.equipment_product_id.price_hour or 0.0) * (line.hours or 1.0),
                        "tax_id": [(6, 0, self.tax_id.ids)],
                    })
                )

        if promotion_value and isinstance(promotion_value,list):
            all_products_data.extend(promotion_value)


        return all_products_data

    def _create_sale_order(self):
        lines = self._prepare_sale_order_lines()
        values = {
            "partner_id": self.player_id.id,
            "reservation_id": self.id,
            'state':'draft',
            "order_line":lines
        }
        order = self.env['sale.order'].create(values)
        if order:
            self.sale_order_id = order.id

    def action_view_sale_order(self):
        self.ensure_one()
        return {
            'name': _('Sales Order'),
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain':[('id','in',self.sale_order_id.ids)],
            'target': 'self',
            'type': 'ir.actions.act_window',
            'context':{'create':False,'edit':False,'delete':False,'copy':False}
        }

    def action_view_invoice(self):
        self.ensure_one()
        invoices = self.invoice_id

        # Include any credit notes (refunds) linked to this invoice
        credit_notes = self.env['account.move'].search([
            ('reversed_entry_id', '=', self.invoice_id.id),
            ('move_type', '=', 'out_refund'),
        ])

        all_invoices = invoices | credit_notes

        return {
            'name': _('Invoices & Refunds'),
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', all_invoices.ids)],
            'target': 'self',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'edit': False, 'delete': False, 'copy': False}
        }

    def action_view_payments(self):
        self.ensure_one()
        move_ids = [self.invoice_id.id]

        # Add credit note(s) created from refund
        credit_notes = self.env['account.move'].search([
            ('reversed_entry_id', '=', self.invoice_id.id),
            ('move_type', '=', 'out_refund'),
        ])
        move_ids += credit_notes.ids

        return {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('invoice_ids', 'in', move_ids)],
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
                'copy': False,
            }
        }

    def action_view_training_sessions(self):
        self.ensure_one()
        return {
            'name': _('Training Sessions'),
            'type': 'ir.actions.act_window',
            'res_model': 'sport.club.training.session',
            'view_mode': 'list,form',
            'domain': [('reservation_id', '=', self.id)],
            'target': 'current',
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
                'copy': False,
            }
        }

    # --------------------------------------------------
    # State Actions
    # --------------------------------------------------

    def action_draft(self):
        self.write({"state": "draft"})

    def action_request(self):
        self._create_sale_order()
        self.promotion_id.usage_count += 1
        self.write({"state": "requested"})

    def action_confirm(self):
        for rec in self:
            sale_order = rec.sale_order_id
            sale_order.action_confirm()
            invoices = sale_order._create_invoices()
            if not invoices:
                raise UserError("Failed to generate invoice from sale order.")

            invoice = invoices[0]
            invoice.action_post()
            rec.invoice_id = invoice.id
            rec.write({"state": "confirmed"})
            rec.generate_qr_code()

    def action_register_payment(self):
        self.ensure_one()

        move_ids = []

        if self.state == 'confirmed':
            if not self.invoice_id:
                raise UserError(_("No invoice found to register a payment."))
            move_ids = [self.invoice_id.id]

        elif self.state == 'refunded':
            credit_note = self.env['account.move'].search([
                ('reversed_entry_id', '=', self.invoice_id.id),
                ('move_type', '=', 'out_refund'),
            ], limit=1)

            if not credit_note:
                raise UserError(_("No credit note found to register a refund payment."))

            move_ids = [credit_note.id]

        else:
            raise UserError(_("You can only register payments for confirmed or refunded reservations."))

        context = {
            'active_model': 'account.move',
            'active_ids': move_ids,
        }

        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'context': context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_check_in(self):
        self.write({"state": "checked_in", "checkin_at": fields.Datetime.now()})

    def action_check_out(self):
        for rec in self:
            rec.write({
                "state": "checked_out",
                "checkout_at": fields.Datetime.now()
            })
            rec._remove_all_attendees_after_checking_out()
            if rec.trainer_id:
                self.env['sport.club.training.session'].sudo()._create_session_from_reservation(rec)

    def action_cancel(self):
        self.write({"state": "cancelled"})
        self._remove_all_attendees_after_checking_out()

    # ============================================================
    # Calendar Domain Builder
    # ============================================================
    def _all_avilable_times(self):
        """
        Build a domain for available calendar time slots based on the selected date,
        club, and facility, excluding already reserved time slots.
        """
        self.ensure_one()

        if not self.date or not self.facility_id:
            return [('id', '=', False)]

        weekday_number = fields.Date.from_string(self.date).weekday()

        current_calendar = self.env['sport.club.calendar'].search([
            ('club_id', '=', self.club_id.id),
            ('facility_id', '=', self.facility_id.id)
        ], limit=1)

        if not current_calendar:
            return [('id', '=', False)]

        # Base domain to fetch slots for the selected day
        domain = [
            ('day_of_week', '=', str(weekday_number)),
            ('calendar_template_id', '=', current_calendar.id),
        ]

        # Search all slots for that day
        all_slots = self.env['sport.club.calendar.line'].search(domain)

        # Find reservations that occupy some slots for the same date + facility + sport
        reservation_domain = [
            ('facility_id', '=', self.facility_id.id),
            ('date', '=', self.date),
            ('state', 'in', ['requested', 'confirmed','checked_in']),
        ]
        if self.sport_id:
            reservation_domain.append(('sport_id', '=', self.sport_id.id))

        existing_reservations = self.env['sport.club.reservation'].search(reservation_domain)

        # Exclude any slots that overlap with existing reservations
        reserved_slot_ids = set()
        for slot in all_slots:
            for res in existing_reservations:
                # Overlap check: slot_from < res_to AND slot_to > res_from
                if slot.start_time < res.time_to and slot.end_time > res.time_from:
                    reserved_slot_ids.add(slot.id)

        # Final domain excludes reserved slots
        if reserved_slot_ids:
            domain.append(('id', 'not in', list(reserved_slot_ids)))

        return domain

    # ============================================================
    # Smart Button / Action
    # ============================================================
    def get_all_avilable_times_for_reservation(self):
        """
        Opens a list view with all available calendar slots that can still be reserved
        for the selected facility, date, and sport.
        """
        self.ensure_one()
        return {
            'name': _('Available Times'),
            'type': 'ir.actions.act_window',
            'res_model': 'sport.club.calendar.line',
            'view_mode': 'list',
            'target': 'new',
            'domain': self._all_avilable_times(),
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
                'copy': False,
                'current_reservation': self.id,
                'default_group_by': 'day_of_week'
            }
        }