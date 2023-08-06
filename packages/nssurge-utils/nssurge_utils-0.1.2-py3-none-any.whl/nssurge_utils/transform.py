from nssurge_utils.parsers import parse_section, unparse_section
from nssurge_utils.utils import sanitize_name, load_countryFlagsNamesAndDialCodes_json


def sanitize_proxy_name(line: str) -> str:
    if (parsed := parse_section(line)) is None:
        # no need to process comments
        return line
    name, values = parsed
    return unparse_section(sanitize_name(name), values) + '\n'


def proxy_name_add_flag_emoji_before_country_code(line: str) -> str:
    if (parsed := parse_section(line)) is None:
        # no need to process comments
        return line
    import re

    name, values = parsed
    countryFlagsNamesAndDialCodes = load_countryFlagsNamesAndDialCodes_json()
    for country_code, country_data in countryFlagsNamesAndDialCodes.items():
        flag_emoji = country_data['flag']
        # name = name.replace(country_code, f'{flag_emoji}-{country_code}')
        name = re.sub(
            rf'(?<=[ |-|^]){country_code}(?=\b|[0-9])',
            rf'{flag_emoji}-{country_code}',
            name,
        )
    return unparse_section(sanitize_name(name), values) + '\n'
