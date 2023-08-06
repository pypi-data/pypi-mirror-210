import base64
import datetime
import decimal

def btoa(s: str) -> bytes:
    utf8_data   = s.encode('utf-8')
    base64_data = base64.b64encode(utf8_data)

    return base64_data.decode('utf-8')

def date_from_string(date_string: str) -> datetime.date:
    return datetime.datetime.strptime(date_string, '%Y%m%d').date()

def pic_to_decimal(number: str, integral_places: int) -> decimal.Decimal:
    integral_part = number[:integral_places]
    decimal_part  = number[integral_places:]

    return decimal.Decimal(integral_part + '.' + decimal_part)

def pic11v99(number: str) -> decimal.Decimal:
    return pic_to_decimal(number, 11)

def pic16v99(number: str) -> decimal.Decimal:
    return pic_to_decimal(number, 16)

def pic7v06(number: str) -> decimal.Decimal:
    return pic_to_decimal(number, 7)