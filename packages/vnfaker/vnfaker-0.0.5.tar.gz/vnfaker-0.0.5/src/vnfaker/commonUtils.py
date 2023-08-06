import random
import math
from calendar import timegm
from datetime import date, datetime
from datetime import timedelta
from datetime import tzinfo
from importlib import resources
from pathlib import Path
from typing import Optional

import orjson


def str_clean(text: str):
    return text.replace(" ", "")


def change_year(current_date: date, year_diff: int) -> date:
    """
    Unless the current_date is February 29th, it is fine to just subtract years.
    If it is a leap day, and we are rolling back to a non-leap year, it will
    cause a ValueError.
    Since this is relatively uncommon, just catch the error and roll forward to
    March 1

    current_date: date  object
    year_diff: int year delta value, positive or negative
    """
    year = current_date.year + year_diff
    try:
        return current_date.replace(year=year)
    except ValueError as e:
        # ValueError thrown if trying to move date to a non-leap year if the current
        # date is February 29th
        if year != 0 and current_date.month == 2 and current_date.day == 29:
            return current_date.replace(month=3, day=1, year=year)
        else:
            raise e


def date_time_ad(
        tzinfo: Optional[tzinfo] = None,
        end_datetime: date = None,
        start_datetime: date = None,
) -> datetime:
    start_time = -62135596800 if start_datetime is None else datetime_to_timestamp(start_datetime)
    end_datetime = datetime_to_timestamp(end_datetime)

    ts = random.randint(start_time, end_datetime)
    return datetime(1970, 1, 1, tzinfo=tzinfo) + timedelta(seconds=ts)


def random_circumference_point(center_point, radius, random_fn=random.random):
    def to_radians(degrees):
        return degrees * math.pi / 180.0

    def to_degrees(radians):
        return radians * 180.0 / math.pi

    EARTH_RADIUS = 6371000  # meters
    TWO_PI = 2 * math.pi
    THREE_PI = 3 * math.pi

    sin_lat = math.sin(to_radians(center_point['latitude']))
    cos_lat = math.cos(to_radians(center_point['latitude']))

    # Random bearing (direction out 360 degrees)
    print(random_fn())
    bearing = random_fn() * TWO_PI
    sin_bearing = math.sin(bearing)
    cos_bearing = math.cos(bearing)

    # Theta is the approximated angular distance
    theta = radius / EARTH_RADIUS
    sin_theta = math.sin(theta)
    cos_theta = math.cos(theta)

    r_latitude = math.asin(sin_lat * cos_theta + cos_lat * sin_theta * cos_bearing)

    r_longitude = (
            to_radians(center_point['longitude'])
            + math.atan2(sin_bearing * sin_theta * cos_lat, cos_theta - sin_lat * math.sin(r_latitude))
    )

    # Normalize longitude L such that -PI < L < +PI
    r_longitude = ((r_longitude + THREE_PI) % TWO_PI) - math.pi

    return {"latitude": to_degrees(r_latitude), "longitude": to_degrees(r_longitude)}


def _read_file(filename, resource):
    resource_name = "vnfaker.data.{}".format(resource)
    with resources.open_text(resource_name, filename) as f:
        data = f.read().split("\n")
    return data


class CommonUtils:
    lastname_filename = "last.name"
    male_filename = "male.name"
    female_filename = "female.name"
    male_mid_filename = "male_middle.name"
    female_mid_filename = "female_middle.name"
    company_filename = "company.name"
    provinces_filename = "flat-divisions.json"
    occupation_filename = "occupation.name"
    sentence_filename = "sentence.txt"
    religion_filename = "religion.name"

    lastNames = _read_file(lastname_filename, "person")
    maleNames = _read_file(male_filename, "person")
    femaleNames = _read_file(female_filename, "person")
    maleMidNames = _read_file(male_mid_filename, "person")
    femaleMidNames = _read_file(female_mid_filename, "person")
    companyNames = _read_file(company_filename, "company")
    occupationNames = _read_file(occupation_filename, "occupation")
    religionNames = _read_file(religion_filename, "religion")
    sentencesValue = _read_file(sentence_filename, "sentence")
    FLAT_DIVISIONS_JSON_PATH = Path(__file__).parent / 'data' / 'provinces' / 'flat-divisions.json'

    address = orjson.loads(FLAT_DIVISIONS_JSON_PATH.read_bytes())
    domainEmail = ['gmail.com',
                   'outlook.com',
                   'yandex.com',
                   'hotmail.com',
                   'icloud.com',
                   'yahoo.com',
                   "abc.com",
                   'vinaconex.com.vn',
                   'zoho.com',
                   'abcd.com',
                   'apollo.edu.vn']


def datetime_to_timestamp(dt: date) -> int:
    return timegm(dt.timetuple())
