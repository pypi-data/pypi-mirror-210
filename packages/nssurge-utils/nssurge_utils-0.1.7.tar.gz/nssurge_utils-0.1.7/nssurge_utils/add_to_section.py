#!/usr/bin/env python3
"""
Author : Xinyuan Chen <45612704+tddschn@users.noreply.github.com>
Date   : 2023-05-27
Purpose: Add lines to a certain section
"""

import argparse
from pathlib import Path
from functools import partial
from pathlib import Path
from nssurge_utils.utils import (
    partition_lines,
    is_section_marker,
    file_line_generator,
    merge_file_partitions,
    put_to_first_if_exist,
    add_to_file_partition,
)
from nssurge_utils.config import (
    surge_config_sections,
    special_proxy_group_value,
    DEFAULT_RULE_TO_PREPEND,
)
from nssurge_utils.parsers import parse_section, unparse_section
from nssurge_utils.predicates import name_contains, value_contains
from nssurge_utils.transform import (
    sanitize_proxy_name,
    proxy_name_add_flag_emoji_before_country_code,
)
from nssurge_utils import __version__


def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Add lines to a certain section',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        'file', metavar='FILE', type=Path, help='Surge config file(s)', nargs='+'
    )
    parser.add_argument(
        '-a',
        '--add',
        metavar='LINE',
        type=str,
        help=" The line to add, if not specified, the default rule will be added to the beginning of the section",
        default=DEFAULT_RULE_TO_PREPEND,
    )
    parser.add_argument(
        '-f',
        '--read-add-from-file',
        metavar='FILE',
        type=Path,
        help='Read lines to add from file',
    )
    parser.add_argument(
        '-s',
        '--section',
        metavar='SECTION',
        type=str,
        default='Rule',
        choices=surge_config_sections,
        help='The section to extract',
    )
    parser.add_argument(
        '-A',
        '--append',
        action='store_true',
        help='Append to the section instead of prepend',
    )
    parser.add_argument(
        '-R',
        '--replace',
        action='store_true',
        help='Replace the section instead of prepend / append',
    )

    parser.add_argument(
        '-C', '--no-comment', action='store_true', help='Do not add comment'
    )

    parser.add_argument(
        '-o',
        '--output',
        metavar='FILE',
        type=Path,
        help='Output file, if not specified, modification will be done in-place',
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
    )

    args = parser.parse_args()
    if not args.output and len(args.file) == 1:
        args.output = args.file[0]
    if args.read_add_from_file:
        args.add = args.read_add_from_file.read_text()
    if args.no_comment:
        args.add = '\n' + args.add + '\n'
    else:
        import shlex, sys
        from datetime import datetime

        # now in iso format
        dt_iso = datetime.now().isoformat()

        args.add = (
            f'\n# Added with command:\n# {shlex.join(sys.argv)}\n# {dt_iso}\n\n'
            + args.add
            + '\n\n'
        )
    return args


def main():
    """Make a jazz noise here"""

    args = get_args()
    if len(args.file) == 1:
        add_to_file_partition(
            to_add=args.add,
            target_file=args.file[0],
            is_first_marker=partial(is_section_marker, section=args.section),
            is_second_marker=is_section_marker,
            prepend=not args.append,
            replace=args.replace,
            output_file=args.output,
        )
    for input_file_path in args.file:
        add_to_file_partition(
            to_add=args.add,
            target_file=input_file_path,
            is_first_marker=partial(is_section_marker, section=args.section),
            is_second_marker=is_section_marker,
            prepend=not args.append,
            replace=args.replace,
        )


if __name__ == '__main__':
    main()
