import re
import json
from datetime import datetime


def is_number(input: str) -> bool:
    trans = str.maketrans("", "", "".join(["-", ".", ","]))
    return str(input).translate(trans).isdigit()


def is_date(input: str) -> bool:
    try:
        date_format = "%d-%m-%Y"
        datetime.strptime(input, date_format)
    except ValueError:
        return False
    return True


def is_valid_geolocation(json_string: str):
    # This line will be excluded from coverage
    # since whatsapp already validate the lat long format
    # pragma: no cover
    try:
        data = json.loads(json_string)
        if isinstance(data, list) and len(data) == 2:
            lat, lng = data
            return is_number(lat) and is_number(lng)
    except (json.JSONDecodeError, ValueError):
        pass
    return False


def is_valid_image(image_type: str) -> bool:
    return image_type in ["image/jpeg", "image/jpg", "image/png", "image/gif"]


def is_valid_string(input: str) -> bool:
    pattern = r'^[a-zA-Z0-9 !\'"\-?,.%&*()+/]+$'
    return bool(re.match(pattern, input))
