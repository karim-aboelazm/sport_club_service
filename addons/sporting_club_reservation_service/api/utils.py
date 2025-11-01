# -*- coding: utf-8 -*-
import pytz
from datetime import datetime
from odoo import _
from odoo.exceptions import UserError, ValidationError, AccessError, MissingError


def convert_to_utc(dt_str, local_tz='Africa/Cairo'):
    if not dt_str:
        return False
    local_zone = pytz.timezone(local_tz)
    naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    localized_dt = local_zone.localize(naive_dt)
    utc_dt = localized_dt.astimezone(pytz.utc)
    return utc_dt.strftime("%Y-%m-%d %H:%M:%S")

def convert_utc_to_local(utc_dt, local_tz='Africa/Cairo'):
    if not utc_dt:
        return False
    local_zone = pytz.timezone(local_tz)

    if isinstance(utc_dt, str):
        utc_dt = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
    utc_zone = pytz.utc
    utc_dt = utc_zone.localize(utc_dt)
    local_dt = utc_dt.astimezone(local_zone)
    return local_dt.strftime("%Y-%m-%d %H:%M:%S")

def get_weekday_code(day_value):
    WEEKDAYS_MAPPING = {
        'monday': '0', 'mon': '0',

        'tuesday': '1', 'tue': '1', 'tues': '1',

        'wednesday': '2', 'wed': '2',

        'thursday': '3', 'thu': '3', 'thur': '3', 'thurs': '3',

        'friday': '4', 'fri': '4',

        'saturday': '5', 'sat': '5',

        'sunday': '6', 'sun': '6',
    }

    if day_value is None:
        raise ValidationError(_("Missing day_of_week value."))

    # Already numeric or stringified number
    if str(day_value) in ['0', '1', '2', '3', '4', '5', '6']:
        return str(day_value)

    if isinstance(day_value, str):
        key = day_value.strip().lower()
        if key in WEEKDAYS_MAPPING:
            return WEEKDAYS_MAPPING[key]
        else:
            valid = ', '.join(sorted(set(WEEKDAYS_MAPPING.keys())))
            raise ValidationError(_(
                "Invalid day name '%s'. Expected one of: %s"
            ) % (day_value, valid))

    raise ValidationError(_(
        "Invalid day_of_week type: %s (must be string or number)." % type(day_value)
    ))

def float_to_time_str_24(float_hour):
    if float_hour is None:
        return ""
    hours = int(float_hour)
    minutes = int(round((float_hour - hours) * 60))
    return f"{hours:02d}:{minutes:02d}"

def float_to_time_str_12(float_hour):
    """Convert float hour (e.g. 13.5) to time string in 12-hour format (e.g. '01:30 PM')."""
    if float_hour is None:
        return ""
    hours = int(float_hour)
    minutes = int(round((float_hour - hours) * 60))

    # Handle rounding edge cases (e.g. 10.999 → 11:00)
    if minutes == 60:
        hours += 1
        minutes = 0

    # Convert to 12-hour format with AM/PM
    suffix = "AM"
    if hours == 0:
        display_hour = 12
    elif hours == 12:
        display_hour = 12
        suffix = "PM"
    elif hours > 12:
        display_hour = hours - 12
        suffix = "PM"
    else:
        display_hour = hours

    return f"{display_hour:02d}:{minutes:02d} {suffix}"

def time_str_to_float(time_str):
    """Convert 'HH:MM' or 'HH:MM AM/PM' into float hours intelligently."""
    if not time_str:
        return None

    s = time_str.strip().lower().replace('.', '').replace(' ', '')
    try:
        # Detect AM/PM automatically
        is_pm = 'pm' in s
        is_am = 'am' in s
        s = s.replace('am', '').replace('pm', '')

        # Split hours and minutes
        if ':' in s:
            hours, minutes = map(int, s.split(':'))
        else:
            hours, minutes = int(s), 0

        # Adjust for 12-hour format
        if is_pm and hours < 12:
            hours += 12
        elif is_am and hours == 12:
            hours = 0

        return hours + minutes / 60.0
    except Exception:
        raise ValueError(f"Invalid time format: {time_str}. Expected 'HH:MM' or 'HH:MM AM/PM'.")
