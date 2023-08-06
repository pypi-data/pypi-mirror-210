from nssurge_utils.parsers import parse_section, unparse_section


def name_contains(
    line: str,
    name_contains: list[str],
    name_not_contain: list[str],
    include_comments: bool = False,
) -> bool:
    if (parsed := parse_section(line)) is None:
        return include_comments
    name, _ = parsed
    return all(n in name for n in name_contains) and all(
        n not in name for n in name_not_contain
    )


def value_contains(
    line: str,
    value_contains: list[str],
    value_not_contain: list[str],
    include_comments: bool = False,
) -> bool:
    if (parsed := parse_section(line)) is None:
        return include_comments
    _, values = parsed
    # return value_contains in values
    return all(any(v in value for value in values) for v in value_contains) and all(
        all(v not in value for value in values) for v in value_not_contain
    )
