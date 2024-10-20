#!/usr/bin/python3
#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

try:
    ## following import success only when file is directly executed from command line
    ## otherwise will throw exception when executing as parameter for "python -m"
    # pylint: disable=W0611
    import __init__
except ImportError:
    ## when import fails then it means that the script was executed indirectly
    ## in this case __init__ is already loaded
    pass

import os
import sys
import argparse
import logging

from clocdirtree import logger
from clocdirtree.clocparser import get_dirs_list, cloc_dirs
from clocdirtree.excludefilter import ExcludeItemFilter
from clocdirtree.graph import generate_graph, store_graph_to_html, set_node_html_attribs, split_to_multi_dict
from clocdirtree.io import write_file, prepare_filesystem_name, read_file


_LOGGER = logging.getLogger(__name__)


# =======================================================================


def process_cloc(args):
    run_dir = args.clocdir
    run_dir = os.path.normpath(run_dir)
    out_dir = args.outdir

    exclude_filter = ExcludeItemFilter(args.exclude)
    dirs_list = []
    potential_dirs_list = get_dirs_list(run_dir, recursive=True)
    potential_dirs_list.insert(0, run_dir)
    for item in potential_dirs_list:
        if exclude_filter.excluded(item):
            continue
        dirs_list.append(item)

    cloc_params_dict = {}
    clocexcludedirs = args.clocexcludedir
    if clocexcludedirs:
        cloc_params_dict["--fullpath"] = None
        cloc_params_dict["--not-match-d"] = "|".join(clocexcludedirs)

    cloc_data_dict = cloc_dirs(dirs_list, cloc_params_dict=cloc_params_dict)
    cloc_data_dict = {item_key.removeprefix(run_dir): item_val for item_key, item_val in cloc_data_dict.items()}

    multi_dict = split_to_multi_dict(cloc_data_dict)
    graph_dir = os.path.join(out_dir, "graphs")
    os.makedirs(graph_dir, exist_ok=True)
    multi_dict_data_list = multi_dict[""]
    key_prefix_list = ["index"]
    generate_page_multidict(multi_dict_data_list, graph_dir, key_prefix_list)

    generate_page_index(out_dir, "graphs/index.html")

    # data_dict = {item_key: item_val[0] for item_key, item_val in cloc_data_dict.items()}
    # graph = generate_graph(data_dict)
    # out_file = os.path.join(out_dir, "full_graph.txt")
    # graph.writeRAW(out_file)


def generate_page_multidict(multi_dict_data_list, out_graph_dir, key_prefix_list):
    value_list = multi_dict_data_list[0]
    cloc_summary = value_list[1]
    multi_dict = multi_dict_data_list[1]

    graph_dict = {}
    for key, data_tuple in multi_dict.items():
        val_list = data_tuple[0]
        if val_list is not None:
            graph_dict[key] = val_list[0]

    base_path_prefix = "/".join(key_prefix_list)
    path_prefix = prepare_filesystem_name(base_path_prefix)

    _LOGGER.info("generating page: %s", path_prefix)

    if graph_dict:
        graph = generate_graph(graph_dict)
        graph.setName(path_prefix)

        node_prefix = path_prefix
        if not node_prefix.endswith("_"):
            node_prefix += "_"
        set_node_html_attribs(graph, node_prefix)
        store_graph_to_html(graph, out_graph_dir)

    generate_page_content(base_path_prefix, path_prefix, cloc_summary, out_graph_dir)

    # go recursive
    for key, data_tuple in multi_dict.items():
        sub_list = key_prefix_list.copy()
        sub_list.append(key)
        generate_page_multidict(data_tuple, out_graph_dir, sub_list)


def generate_page_index(out_dir, redirect_link):
    content = f"""\
<!DOCTYPE HTML>
<!--
File was automatically generated using 'cloc-directory-tree' project.
Project is distributed under the BSD 3-Clause license.
-->
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url={redirect_link}">

    <title>cloc view</title>
    <style>
        body {{  padding: 24;
                background-color: #bbbbbb;
             }}
    </style>
</head>
<body>
    <!-- Note: don't tell people to `click` the link, just tell them that it is a link. -->
    If you are not redirected automatically, follow this <a href='{redirect_link}'>link to example</a>.
</body>
</html>
"""
    out_file = os.path.join(out_dir, "index.html")
    _LOGGER.info("writing index page: %s", out_file)
    write_file(out_file, content)


def generate_page_content(directory, path_prefix, cloc_summary, out_graph_dir):
    map_path = os.path.join(out_graph_dir, f"{path_prefix}.map")
    map_content = read_file(map_path)

    img_content = ""
    if map_content:
        img_content = f"""\
        <img src="{path_prefix}.png" alt="graph" usemap="#{path_prefix}">
{map_content}
"""
    else:
        img_content = "no subdirs with results"

    content = f"""\
<!DOCTYPE HTML>
<!--
File was automatically generated using 'cloc-directory-tree' project.
Project is distributed under the BSD 3-Clause license.
-->
<html>
<head>
    <title>cloc view</title>
    <style>
        body {{
                background-color: #bbbbbb;
             }}

        pre {{  background-color: rgb(226, 226, 226);
               margin: 0px;
               padding: 16px;
            }}

        pre code {{  margin: 0px;
                    padding: 0px;
                 }}

        .section {{
            margin-bottom: 12px;
        }}

        .graphsection img {{
        }}

        .clocsection {{
            float: left;
        }}
    </style>
</head>
<body>
    <div class="section"><a href="../index.html">Back to Index</a></div>
    <div class="section">{directory}</div>
    <div class="graphsection section">
{img_content}
    </div>
    <pre class="clocsection section">{cloc_summary}</pre>
</body>
</html>
"""

    out_file = os.path.join(out_graph_dir, f"{path_prefix}.html")
    write_file(out_file, content)


# =======================================================================


def main():
    parser = argparse.ArgumentParser(
        prog="python3 -m clocdirtree.main",
        description="dump cloc data and navigate it as directory tree",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-la", "--logall", action="store_true", help="Log all messages")
    parser.set_defaults(func=process_cloc)
    parser.add_argument("--clocdir", action="store", required=True, default="", help="Directory to analyze by 'cloc'")
    parser.add_argument("--outdir", action="store", required=True, default="", help="Output directory")
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=[],
        help="Space separated list of items to exclude. e.g. --exclude '/usr/*' '*/tmp/*'",
    )
    parser.add_argument(
        "--clocexcludedir",
        nargs="+",
        default=[],
        help="Space separated list of dirs to exclude by cloc itself. e.g. --exclude 'usr' 'tmp'",
    )

    ## =================================================

    args = parser.parse_args()

    if args.logall is True:
        logger.configure(logLevel=logging.DEBUG)
    else:
        logger.configure(logLevel=logging.INFO)

    if "func" not in args or args.func is None:
        ## no command given -- print help message
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    code = main()
    sys.exit(code)
