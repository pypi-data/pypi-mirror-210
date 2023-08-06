#!/usr/bin/env python3
"""
Author : Xinyuan Chen <45612704+tddschn@users.noreply.github.com>
Date   : 2023-05-24
Purpose: Extract the [Proxy] section from a Surge config file
"""

import argparse
from functools import partial
from pathlib import Path
from nssurge_utils.utils import (
    partition_lines,
    is_section_marker,
    file_line_generator,
    merge_file_partitions,
    put_to_first_if_exist,
)
from nssurge_utils.config import surge_config_sections, special_proxy_group_value
from nssurge_utils.parsers import parse_section, unparse_section
from nssurge_utils.predicates import name_contains, value_contains
from nssurge_utils.transform import (
    sanitize_proxy_name,
    proxy_name_add_flag_emoji_before_country_code,
)


def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Extract the [Proxy] section from a Surge config file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        'file', metavar='FILE', type=Path, help='Surge config file(s)', nargs='+'
    )
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
    parser.add_argument(
        '-n',
        '--name-contains',
        metavar='STRING',
        type=str,
        help='Filter by name',
        nargs='+',
        default=[],
    )
    parser.add_argument(
        '-v',
        '--value-contains',
        metavar='STRING',
        type=str,
        help='Filter by value',
        nargs='+',
        default=[],
    )
    parser.add_argument(
        '-N', '--name-not-contain', metavar='STRING', type=str, nargs='+', default=[]
    )
    parser.add_argument(
        '-V', '--value-not-contain', metavar='STRING', type=str, nargs='+', default=[]
    )

    parser.add_argument(
        '-S', '--sanitize', action='store_true', help='Sanitize the proxy names'
    )

    parser.add_argument(
        '-f',
        '--add-flag-emoji',
        action='store_true',
        help='Add flag emoji to proxy names',
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
    partition_lines_kwargs = {}
    partition_lines_kwargs['inclusion_predicate'] = lambda line: name_contains(
        line=line,
        name_contains=args.name_contains,
        name_not_contain=args.name_not_contain,
    ) and value_contains(
        line=line,
        value_contains=args.value_contains,
        value_not_contain=args.value_not_contain,
    )
    if args.sanitize and args.add_flag_emoji:
        partition_lines_kwargs[
            'transform_fn'
        ] = lambda line: proxy_name_add_flag_emoji_before_country_code(
            sanitize_proxy_name(line)
        )
    elif args.sanitize:
        partition_lines_kwargs['transform_fn'] = sanitize_proxy_name
    elif args.add_flag_emoji:
        partition_lines_kwargs[
            'transform_fn'
        ] = proxy_name_add_flag_emoji_before_country_code

    if args.add_to_proxy:
        for input_file_path in args.file:
            merge_file_partitions(
                input_file=input_file_path,
                target_file=args.add_to_proxy,
                is_first_marker_input=partial(is_section_marker, section=args.section),
                is_second_marker_input=is_section_marker,
                is_first_marker_output=partial(is_section_marker, section='Proxy'),
                is_second_marker_output=is_section_marker,
                output_file=args.output,
                **partition_lines_kwargs,
            )
            if args.add_to_proxy_group:
                _, extracted_lines_input, _ = partition_lines(
                    file_line_generator(input_file_path),
                    is_first_marker=partial(is_section_marker, section=args.section),
                    is_second_marker=is_section_marker,
                    **partition_lines_kwargs,
                )
                # partition_lines_kwargs_without_filter = partition_lines_kwargs.copy()
                # if 'inclusion_predicate' in partition_lines_kwargs_without_filter:
                #     partition_lines_kwargs_without_filter.pop('inclusion_predicate')
                lines_before, extracted_lines_target, lines_after = partition_lines(
                    file_line_generator(args.output),
                    is_first_marker=partial(is_section_marker, section='Proxy Group'),
                    is_second_marker=is_section_marker,
                    # **partition_lines_kwargs_without_filter,
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
                    # default_selected_policy = proxy_group_values[1]
                    # preserve default_selected_policy
                    new_proxy_group_rule = unparse_section(
                        proxy_group_name,
                        put_to_first_if_exist(
                            put_to_first_if_exist(
                                (proxy_names + proxy_group_values),
                                {proxy_group_values[1]}
                                if len(proxy_group_values) > 1
                                else set(),
                            ),
                            special_proxy_group_value,
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

    for input_file_path in args.file:
        _, extracted_lines_input, _ = partition_lines(
            file_line_generator(input_file_path),
            is_first_marker=partial(is_section_marker, section=args.section),
            is_second_marker=is_section_marker,
            **partition_lines_kwargs,
        )
        print(f'# {input_file_path.resolve()}')
        print(''.join(extracted_lines_input), end='')


if __name__ == '__main__':
    main()
