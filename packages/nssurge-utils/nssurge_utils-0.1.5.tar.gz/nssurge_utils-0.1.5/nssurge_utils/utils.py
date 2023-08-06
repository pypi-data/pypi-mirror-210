from functools import cache
from os import PathLike
from nssurge_utils.types import SurgeConfigSections
from typing import Callable, Generator, Literal, Tuple


def file_line_generator(file_path: PathLike) -> Generator[str, None, None]:
    with open(file_path, 'r') as file:
        for line in file:
            yield line


def partition_lines(
    line_gen: Generator[str, None, None],
    is_first_marker: Callable[[str], bool],
    is_second_marker: Callable[[str], bool],
    include_markers: Tuple[bool, bool] = (False, False),
    inclusion_predicate: Callable[[str], bool] = lambda _: True,
    transform_fn: Callable[[str], str] = lambda line: line,
) -> tuple[list[str], list[str], list[str]]:
    lines_before = []
    lines_in_between = []
    lines_after = []
    # before_in_between = True
    # in_between = False
    location: Literal['before', 1, 'between', 2, 'after'] = 'before'

    for line in line_gen:
        match location:
            case 'before':
                if is_first_marker(line):
                    if include_markers[0]:
                        lines_in_between.append(line)
                    else:
                        lines_before.append(line)
                    location = 1
                else:
                    lines_before.append(line)
            case 1 | 'between':
                if is_second_marker(line):
                    if include_markers[1]:
                        lines_in_between.append(line)
                    else:
                        lines_after.append(line)
                    location = 2
                else:
                    lines_in_between.append(line)
                    location = 'between'
            case 2 | 'after':
                lines_after.append(line)
                location = 'after'
    return (
        lines_before,
        [transform_fn(x) for x in filter(inclusion_predicate, lines_in_between)],
        lines_after,
    )


def is_section_marker(line: str, section: SurgeConfigSections | None = None) -> bool:
    import re

    if section is None:
        return re.match(r'^\[(.*)\]', line) is not None
    return re.match(r'^\[' + section + r'\]', line) is not None


def merge_file_partitions(
    input_file: PathLike,
    target_file: PathLike,
    is_first_marker_input: Callable[[str], bool],
    is_second_marker_input: Callable[[str], bool],
    is_first_marker_output: Callable[[str], bool],
    is_second_marker_output: Callable[[str], bool],
    inclusion_predicate: Callable[[str], bool] = lambda _: True,
    transform_fn: Callable[[str], str] = lambda line: line,
    prepend: bool = True,
    replace: bool = False,
    output_file: PathLike | None = None,
) -> None:
    # Extract lines from input file
    _, extracted_input_lines, _ = partition_lines(
        file_line_generator(input_file),
        is_first_marker_input,
        is_second_marker_input,
        include_markers=(False, False),
        inclusion_predicate=inclusion_predicate,
        transform_fn=transform_fn,
    )

    # Process output file
    target_lines = partition_lines(
        file_line_generator(target_file),
        is_first_marker_output,
        is_second_marker_output,
        include_markers=(False, False),
        # transform_fn=transform_fn,
    )
    if replace:
        replaced_lines = extracted_input_lines
    elif prepend:
        replaced_lines = extracted_input_lines + target_lines[1]
    else:
        replaced_lines = target_lines[1] + extracted_input_lines
    output_lines = target_lines[0] + replaced_lines + target_lines[2]
    if output_file is None:
        output_file = target_file
    with open(output_file, 'w') as file:
        file.writelines(output_lines)


def put_to_first_if_exist(l: list, members: set) -> list:
    """
    For Proxy Group rule values

    write a python function put_to_first_if_exist(l: list, members: set) -> list
    That check if any member of  members exists in l, if yes, remove all other members in l if exists, and make sure to put the member to the first in the output list, and make sure there’s no duplicate of this member in the output list.

    the output list should contain at most 1 member, and if it contain a member, the member should be at index 0, and there’s no duplicate.
    """
    members_exist_in_l = {member for member in members if member in l}
    if len(members_exist_in_l) >= 1:
        selected_member = members_exist_in_l.pop()
        # remove any other members in l if exists
        l = [x for x in l if x not in members]
        # put the member to the first in the output list
        l.insert(0, selected_member)
        return l
    else:
        return l


@cache
def load_countryFlagsNamesAndDialCodes_json() -> dict[str, dict[str, str]]:
    from nssurge_utils.config import countryFlagsNamesAndDialCodes_json_path
    import json

    with open(countryFlagsNamesAndDialCodes_json_path, 'r') as file:
        return json.load(file)


def sanitize_name(name: str) -> str:
    import re

    name = re.sub(r'中国上海', 'cn-shanghai', name)
    name = re.sub(r'中国北京', 'cn-beijing', name)
    name = re.sub(r'中国徐州', 'cn-xuzhou', name)
    name = re.sub(r'俄罗斯', 'ru', name)
    name = re.sub(r'印度', 'in', name)
    name = re.sub(r'台湾', 'tw', name)
    name = re.sub(r'土耳其', 'tr', name)
    name = re.sub(r'德国', 'de', name)
    name = re.sub(r'新加坡', 'sg', name)
    name = re.sub(r'日本', 'jp', name)
    name = re.sub(r'澳大利亚', 'au', name)
    name = re.sub(r'澳门', 'mo', name)
    name = re.sub(r'美国', 'us', name)
    name = re.sub(r'菲律宾', 'ph', name)
    name = re.sub(r'韩国', 'kr', name)
    name = re.sub(r'香港', 'hk', name)
    name = re.sub(r'英国', 'uk', name)
    name = re.sub(r'加拿大', 'ca', name)
    name = re.sub(r'巴西', 'br', name)
    name = re.sub(r'意大利', 'it', name)
    name = re.sub(r'匈牙利', 'hu', name)
    name = re.sub(r'阿联酋', 'ae', name)
    name = re.sub(r'法国', 'fr', name)
    name = re.sub(r'阿根廷', 'ar', name)
    # 泰国, 荷兰
    name = re.sub(r'泰国', 'th', name)
    name = re.sub(r'荷兰', 'nl', name)

    # 游戏 - gaming
    name = re.sub(r'游戏', 'gaming', name)

    # 福利
    name = re.sub(r'福利', 'benefits', name)
    # 中转 - relay
    name = re.sub(r'中转', 'relay', name)
    # 原生 - native
    name = re.sub(r'原生', 'native', name)
    # 动态 - dynamic
    name = re.sub(r'动态', 'dynamic', name)
    # 专线 - dedicated
    name = re.sub(r'专线', ' dedicated', name)
    #  ) - )
    name = re.sub(r' \)', ')', name)
    # 广日 - gz-jp
    name = re.sub(r'广日', 'gz->jp', name)
    # 广港
    name = re.sub(r'广港', 'gz->hk', name)
    # 广新
    name = re.sub(r'广新', 'gz->sg', name)
    # 广台
    name = re.sub(r'广台', 'gz->tw', name)
    # 广美
    name = re.sub(r'广美', 'gz->us', name)
    # 下载专用
    name = re.sub(r'下载专用', 'download optimized', name)
    # 支持
    name = re.sub(r'支持', 'supports', name)
    # 大流量
    name = re.sub(r'大流量', 'high bandwidth', name)
    # 限速
    name = re.sub(r'限速', 'limit ', name)

    # Flags: cn -> tw
    name = re.sub(r'🇨🇳 tw', '🇹🇼 tw', name)

    # cSpell:disable
    # dlersedmark
    # cSpell:enable
    name = re.sub(r'标准', '-standard', name)
    name = re.sub(r'高级', '-premium', name)

    name = re.sub(
        r'专线', '', name
    )  # all iplc (gold) has this in their name, so it's useless
    # name = re.sub(r'专线', '-dedicated', name)

    name = re.sub(r'--临时', '-temporary', name)
    name = re.sub(r'--测试', '-testing', name)

    # Relay nodes with '-->' breaks the code
    name = re.sub(r'->', '--', name)

    return name
