import phonenumbers


def parse_nr(input_phone_number, local_country="SE", fail_as_none=False) -> str | None:
    """Check for valid phone number and will always return it in pared E164 format

    Args:
        input_phone_number (str): The phonenumber
            It ignores punctuation and white-space, as
            well as any text before the number (e.g. a leading "Tel: ") and trims
            the non-number bits.  It will accept a number in any format (E164,
            national, international etc), assuming it can be interpreted with the
            defaultRegion supplied. It also attempts to convert any alpha characters
            into digits if it thinks this is a vanity number of the type "1800
            GOT MILK".

        local_country (str, optional) ISO 3166-1 alpha-2, All Caps, Default=SE (Sweden)
            This what country to try to parse local number by, This should be the country
            you are receiving most of the users from.
            see: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements

        fail_as_none (bool, optional): Will catch error internally and return None insted

    Raises:
        ValueError if invalid phonenumber

    Return:
        Valid phonenumber in E164 format as a string

    Examples:
        >>> parse_nr("+46701234567")
        '+46701234567'
        >>> parse_nr("0701234567")
        '+46701234567'
        >>> parse_nr("1800 GOT MILK", local_country="US")
        '+18004686455'

    """
    try:
        if not isinstance(input_phone_number, str):
            raise ValueError
        nr = phonenumbers.parse(input_phone_number, region=local_country)
        if phonenumbers.is_valid_number(nr):
            return str(
                phonenumbers.format_number(nr, phonenumbers.PhoneNumberFormat.E164)
            )
        else:
            raise ValueError
    except (ValueError, phonenumbers.phonenumberutil.NumberParseException) as e:
        if fail_as_none:
            return None
        else:
            raise ValueError(f"{input_phone_number!r} is not vaild") from e
