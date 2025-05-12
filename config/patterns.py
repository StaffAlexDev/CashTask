import re

COUNT_DAYS = {1, 2, 7, 14}

INVOICE_PATTERN = re.compile(
    r"(?P<amount>[+-]?\d{1,5})\s+(?P<payment_type>[^\s,]+)\s*,?\s*(?P<description>.+\S)",
    re.IGNORECASE
)

PAYMENT_TYPE_PATTERNS = {
    "нал": ["нал", "налл", "налик", "нл", "cash", ],
    "безнал": ["безнал", "бнал", "бзнал", "бзнл", "бз", "card", "transfer", "bank", "перевод", "картой"]
}

NAME_PATTERN = r'^[a-zA-Zа-яА-ЯёЁ\-]{2,20}(?:\s[a-zA-Zа-яА-ЯёЁ\-]{2,20})?$'
PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$", re.IGNORECASE)

BRAND_PATTERN = r"^[\w\s\-]{2,30}$"
MODEL_PATTERN = r"^[\w\s\-]{2,40}$"
VIN_PATTERN = r"^[A-HJ-NPR-Z0-9]{17}$"

DATE_PATTERN = r"^\d{2}\.\d{2}\.\d{4}$"

LICENSE_PLATE_PATTERNS = [
        # Литва, Латвия, Польша (AB1234, ABC123, 1234AB)
        r'^[A-Z]{2,3}\d{2,5}$',
        r'^\d{2,4}[A-Z]{2,3}$',

        # Германия, Франция (AB-123-CD, B XY 1234)
        r'^[A-Z]{1,3}\d{1,4}[A-Z]{0,2}$',

        # Временные номера (L123456, TR12345)
        r'^[A-Z]{1,2}\d{5,6}$',

        # Украина (AA1234BB)
        r'^[A-Z]{2}\d{4}[A-Z]{2}$',

        # Беларусь (1234AB1)
        r'^\d{4}[A-Z]{2}[1-7]$'
    ]

SOCIAL_PATTERN = r'''
        ^(?:https?:\/\/)?
        (?:www\.)?
        (?:
            telegram\.me|t\.me|
            instagram\.com|
            wa\.me|
            viber\.com|
            tiktok\.com|
            facebook\.com|
            twitter\.com|x\.com
        )
        \/[a-zA-Z0-9_\-\.]{1,30}\/?$
        |
        ^@[a-zA-Z0-9_\-\.]{3,30}$
    '''
