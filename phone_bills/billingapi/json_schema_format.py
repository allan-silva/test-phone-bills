from jsonschema import draft4_format_checker
from phone_bills.billingcommon.util import extract_phone_number


@draft4_format_checker.checks('phone-number')
def is_phone_number(val):
    try:
        _, _ = extract_phone_number(val)
        return True
    except Exception:
        return False
