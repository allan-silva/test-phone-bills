import re

from jsonschema import draft4_format_checker


PHONE_NUMBER_RE = re.compile('^[0-9]{2}[0-9]{8,9}$')


@draft4_format_checker.checks('phone-number')
def is_phone_number(val):
    return PHONE_NUMBER_RE.match(val)
