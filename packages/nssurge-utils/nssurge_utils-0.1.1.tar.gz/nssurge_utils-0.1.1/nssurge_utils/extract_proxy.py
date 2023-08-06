#!/usr/bin/env python3
"""
Author : Xinyuan Chen <45612704+tddschn@users.noreply.github.com>
Date   : 2023-05-24
Purpose: Extract the [Proxy] section from a Surge config file
"""

import argparse
from functools import partial
from pathlib import Path
from pprint import pprint
from nssurge_utils.utils import (
    partition_lines,
    is_section_marker,
    file_line_generator,
    merge_file_partitions,
    put_to_first_if_exist,
)
from nssurge_utils.config import surge_config_sections, special_proxy_group_value
from nssurge_utils.parsers import parse_section, unparse_section


def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Extract the [Proxy] section from a Surge config file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('file', metavar='FILE', type=Path, help='Surge config file')
    parser.add_argument(
        '-s',
        '--section',
        metavar='SECTION',
        type=str,
        default='Proxy',
        choices=surge_config_sections,
        help='The section to extract',
    )
    parser.add_argument(
        '--add-to-proxy',
        metavar='FILE',
        type=Path,
        help='Add the extracted proxy config to the proxy section of file',
    )
    parser.add_argument(
        '--add-to-proxy-group',
        action='store_true',
        help='Add the extracted proxy names to the proxy group section of file',
    )
    parser.add_argument(
        '-o',
        '--output',
        metavar='FILE',
        type=Path,
        help='Output file, if not specified, modification will be done in-place',
    )

    args = parser.parse_args()
    if args.add_to_proxy_group and not args.add_to_proxy:
        parser.error(
            '--add-to-proxy-group requires --add-to-proxy to be specified as well'
        )
    if not args.output:
        args.output = args.add_to_proxy
    return args


def main():
    """Make a jazz noise here"""

    args = get_args()
    if args.add_to_proxy:
        merge_file_partitions(
            input_file=args.file,
            target_file=args.add_to_proxy,
            is_first_marker_input=partial(is_section_marker, section=args.section),
            is_second_marker_input=is_section_marker,
            is_first_marker_output=is_section_marker,
            is_second_marker_output=is_section_marker,
            output_file=args.output,
        )
        if args.add_to_proxy_group:
            _, extracted_lines_input, _ = partition_lines(
                file_line_generator(args.file),
                is_first_marker=partial(is_section_marker, section=args.section),
                is_second_marker=is_section_marker,
            )
            lines_before, extracted_lines_target, lines_after = partition_lines(
                file_line_generator(args.output),
                is_first_marker=partial(is_section_marker, section='Proxy Group'),
                is_second_marker=is_section_marker,
            )
            proxy_names = []
            for proxy_rule in extracted_lines_input:
                if (parsed := parse_section(proxy_rule)) is None:
                    continue
                proxy_name, _ = parsed
                proxy_names.append(proxy_name)

            new_proxy_group_rules = []
            for proxy_group_rule in extracted_lines_target:
                if (parsed := parse_section(proxy_group_rule)) is None:
                    continue
                proxy_group_name, proxy_group_values = parsed
                new_proxy_group_rule = unparse_section(
                    proxy_group_name,
                    put_to_first_if_exist(
                        proxy_names + proxy_group_values, special_proxy_group_value
                    ),
                    section='Proxy Group',
                )
                new_proxy_group_rules.append(new_proxy_group_rule + '\n')
            # write lines_before, new_proxy_group_rules, lines_after to output_file
            with open(args.output, 'w') as f:
                f.writelines(lines_before)
                f.writelines(new_proxy_group_rules)
                f.writelines(lines_after)
        return

    _, extracted_lines_input, _ = partition_lines(
        file_line_generator(args.file),
        is_first_marker=partial(is_section_marker, section=args.section),
        is_second_marker=is_section_marker,
    )
    print(''.join(extracted_lines_input), end='')


if __name__ == '__main__':
    main()
