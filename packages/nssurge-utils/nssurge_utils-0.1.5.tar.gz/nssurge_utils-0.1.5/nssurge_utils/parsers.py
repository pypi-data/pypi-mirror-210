import re
from nssurge_utils.types import SurgeConfigSections


def get_sep_delim(section):
    match section:
        case 'Rule':
            value_delimiter = ','
            name_value_separator = ','
            # 1. normal rule
            # # >> Tencent AIA
            # IP-CIDR,162.14.0.0/18,no-resolve
            # 2. rule set
            # RULE-SET,https://ruleset.skk.moe/List/non_ip/global.conf,Proxy
        case 'URL Rewrite':
            # examples
            # cSpell:disable
            # ^http://\[::\] http://127.0.0.1 302
            # ^https?:\/\/cdn\.fivecdm\.com\/cr\/ - reject
            # cSpell:enable
            value_delimiter = ' '
            name_value_separator = ' '
        case _:
            value_delimiter = ','
            name_value_separator = '='
    return value_delimiter, name_value_separator


def parse_section(
    line: str, section: SurgeConfigSections | None = None
) -> tuple[str, list[str]] | None:
    comment_markers = '#'
    if line.startswith(comment_markers) or line.strip() == '':
        return None
    value_delimiter, name_value_separator = get_sep_delim(section)
    # first partition line using name_value_separator
    name, value = line.partition(name_value_separator)[::2]
    name = name.strip()
    value = value.strip()
    # then partition value using value_delimiter
    values = [x.strip() for x in value.split(value_delimiter)]
    return name, values


def unparse_section(
    name: str, values: list[str], section: SurgeConfigSections | None = None
) -> str:
    value_delimiter, name_value_separator = get_sep_delim(section)
    value_str = f'{value_delimiter} '.join(values)
    section_str = f"{name}{name_value_separator if name_value_separator == ',' else f' {name_value_separator} '}{value_str}"
    return section_str
