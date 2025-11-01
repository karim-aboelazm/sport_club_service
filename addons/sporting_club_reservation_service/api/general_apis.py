from .utils import *
from odoo.exceptions import ValidationError
from odoo import api, models, _

to_dict = {
    "all_cities": [],
    "all_areas": [],
    "all_clubs": [],
    "all_sports": [],
    "all_facilities": [],
    "all_calendars": [],
    "all_policies": [],
    "all_promotions": [],
    "all_partners_players": [],
    "all_partners_trainers": [],
    "all_users_owner": [],
    "all_products_equipments": []
}

class ProjectGeneralApi(models.AbstractModel):
    _name = 'project.general.api'
    _description = "General API Helper"


    @api.model
    def fetch_all_data(self):
        try:
            Country = self.env.ref('base.eg')
        except ValueError:
            raise ValidationError("Country 'Egypt' not found by external ID 'base.eg'.")

        # Cities in Egypt
        City = self.env['res.country.state.cities'].sudo().search([('state_id.country_id', '=', Country.id)])
        to_dict['all_cities'] = [{
            "id": c.id,
            "name_en": c.name_en,
            "name_ar": c.name_ar,
            "state_id": {
                "id": c.state_id.id,
                "name": c.state_id.display_name
            } if c.state_id else {}
        } for c in City]

        # Areas in Egypt
        Area = self.env['res.country.state.cities.areas'].sudo().search([('state_id.country_id', '=', Country.id)])
        to_dict['all_areas'] = [{
            "id": a.id,
            "name": a.name,
            "city_id": {
                "id": a.city_id.id,
                "name_en": a.city_id.name_en,
                "name_ar": a.city_id.name_ar
            } if a.city_id else {},
            "state_id": {
                "id": a.state_id.id,
                "name": a.state_id.display_name
            } if a.state_id else {}
        } for a in Area]

        # Clubs
        Club = self.env['sport.club.model'].sudo()
        to_dict['all_clubs'] = Club._api_search_clubs()

        # Sports
        Sport = self.env['sport.club.sports'].sudo()
        to_dict['all_sports'] = Sport._api_search_sports()

        # Facilities
        Facility = self.env['sport.club.facility'].sudo()
        to_dict['all_facilities'] = Facility._api_search_facilities()

        # Calendars
        Calendar = self.env['sport.club.calendar'].sudo()
        to_dict['all_calendars'] = Calendar._api_search_calendars()
        # Policies
        Policy = self.env['sport.club.policy'].sudo()
        to_dict['all_policies'] = Policy._api_search_policies()

        # Promotions
        Promotion = self.env['sport.club.promotion'].sudo()
        to_dict['all_promotions'] = Promotion._api_search_promotions()

        # Players
        Players = self.env['res.partner'].sudo().search([('is_player', '=', True)])
        to_dict['all_partners_players'] = [{
            "id": p.id,
            "name": p.display_name,
            "email": p.email,
            "mobile": getattr(p, 'mobile', False),
            "phone": getattr(p, 'phone', False),
        } for p in Players]

        # Trainers
        Trainers = self.env['sport.club.trainer'].sudo().search([])
        to_dict['all_partners_trainers'] = Trainers._api_search_trainers()

        # Users / Owners
        Users = self.env['res.users'].sudo().search([('is_club_owner','=',True)])
        to_dict['all_users_owner'] = [{
            "id": u.id,
            "name": u.display_name,
            "email": u.partner_id.email,
            "mobile":u.partner_id.mobile,
            "phone":u.partner_id.phone,
        } for u in Users]

        # Products / Equipments
        Products = self.env['product.product'].sudo().search([('is_equipment', '=', True)])
        to_dict['all_products_equipments'] = [{
            "id": eq.id,
            "name": eq.display_name,
            "price_hour":eq.price_hour,
            "club_id":{
                "id":eq.club_id.id,
                "name":eq.club_id.name
            },
            "sport_id":{
                "id":eq.sport_id.id,
                "name":eq.sport_id.name
            },
        } for eq in Products]

        return to_dict