#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import logging

import re
import json
import subprocess  # nosec

# from multiprocessing import Pool
from multiprocessing.pool import ThreadPool as Pool

from clocdirtree.io import read_file


_LOGGER = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


## ===================================================================


def run_cloc(cloc_dir, out_path, recursive=False):
    """Run cloc recursively on given directory and write results to given path."""
    dirs_list = get_dirs_list(cloc_dir, recursive)
    data_dir = cloc_dirs(dirs_list)
    with open(out_path, "w", encoding="utf8") as json_file:
        json.dump(data_dir, json_file, allow_nan=False)


def get_dirs_list(start_dir, recursive=False):
    if recursive:
        dirs_list = []
        for walk_item in os.walk(start_dir):
            item_root = walk_item[0]
            sub_list = [os.path.join(item_root, item) for item in walk_item[1]]
            dirs_list.extend(sub_list)
        return dirs_list

    sub_dirs = next(os.walk(start_dir))[1]
    dirs_list = []
    for subdir in sub_dirs:
        sub_path = os.path.join(start_dir, subdir)
        dirs_list.append(sub_path)
    return dirs_list


def cloc_dirs(dirs_list, exclude_languages=None):
    """Run cloc against given list of directory paths."""
    _LOGGER.info("checking directories:\n%s", "\n".join(dirs_list))
    ret_dict = {}
    with Pool() as process_pool:
        # with Pool(processes=1) as process_pool:
        result_queue = []

        for dir_path in dirs_list:
            async_result = process_pool.apply_async(cloc_directory, [dir_path, exclude_languages])
            result_queue.append((dir_path, async_result))

        # wait for results
        for dir_path, async_result in result_queue:
            lines, content = async_result.get()
            if lines < 1:
                continue
            ret_dict[dir_path] = [lines, content]

    return ret_dict


def cloc_directory(sources_dir, exclude_languages=None):
    _LOGGER.info(f"counting code on: {sources_dir}")  # pylint: disable=W1203

    if exclude_languages is None:
        exclude_languages = []

    if os.path.islink(sources_dir):
        result = subprocess.run(  # nosec
            ["cloc", "--sum-one", "--follow-links", sources_dir], capture_output=True, check=True
        )
    else:
        result = subprocess.run(["cloc", "--sum-one", sources_dir], capture_output=True, check=True)  # nosec

    output = result.stdout.decode("utf-8")
    output = output.splitlines()
    output = output[1:]
    output = "\n".join(output)

    ## _LOGGER.info( "cloc output:\n%s", output )

    overall_code = parse_code(output)
    exclude_sum = 0
    for item in exclude_languages:
        exclude_sum += parse_code(output, item)
    return overall_code - exclude_sum, output


def parse_cloc_file(file_path, language="SUM:", ignore=None):
    if ignore is None:
        ignore = []
    try:
        content = read_file(file_path)
        language_lines = parse_code(content, language=language)
        ignore_sum = 0
        for ignore_item in ignore:
            ignore_lines = parse_code(content, language=ignore_item)
            if ignore_lines > 0:
                ignore_sum += ignore_lines
        return language_lines - ignore_sum
    except BaseException:
        _LOGGER.error("error while loading file: %s content:\n%s", file_path, content)
        raise


def parse_code(content, language="SUM:"):
    for line in content.splitlines():
        if len(line) < 1:
            continue
        if line.startswith(language):
            ## dependency
            pattern = "^" + language + r"\D*(\d*)\s*(\d*)\s*(\d*)\s*(\d*)\s*$"
            matched = re.findall(pattern, line)
            if len(matched) != 1:
                _LOGGER.warning("invalid state for line: %s", line)
                continue
            result = matched[0]
            if len(result) != 4:
                _LOGGER.warning("invalid state for line: %s", line)
                continue
            return int(result[3])
    return -1
