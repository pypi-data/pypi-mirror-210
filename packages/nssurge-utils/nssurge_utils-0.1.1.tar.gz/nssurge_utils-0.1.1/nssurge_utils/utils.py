from os import PathLike
from nssurge_utils.types import SurgeConfigSections
from typing import Callable, Generator, List, Literal, Tuple


def file_line_generator(file_path: PathLike) -> Generator[str, None, None]:
    with open(file_path, 'r') as file:
        for line in file:
            yield line


def partition_lines(
    line_gen: Generator[str, None, None],
    is_first_marker: Callable[[str], bool],
    is_second_marker: Callable[[str], bool],
    include_markers: Tuple[bool, bool] = (False, False),
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
    return lines_before, lines_in_between, lines_after


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
    )

    # Process output file
    target_lines = partition_lines(
        file_line_generator(target_file),
        is_first_marker_output,
        is_second_marker_output,
        include_markers=(False, False),
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
