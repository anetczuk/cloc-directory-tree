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


def cloc_dirs(dirs_list, exclude_languages=None, cloc_params_dict=None):
    """Run cloc against given list of directory paths."""
    _LOGGER.info("checking directories:\n%s", "\n".join(dirs_list))
    ret_dict = {}
    with Pool() as process_pool:
        # with Pool(processes=1) as process_pool:
        result_queue = []

        for dir_path in dirs_list:
            async_result = process_pool.apply_async(
                execute_cloc, [dir_path, "raw", exclude_languages, cloc_params_dict]
            )
            result_queue.append((dir_path, async_result))

        # wait for results
        for dir_path, async_result in result_queue:
            lines, content = async_result.get()
            if lines < 1:
                continue
            ret_dict[dir_path] = [lines, content]

    return ret_dict


def execute_cloc(sources_dir, mode, exclude_languages=None, cloc_params_dict=None):
    _LOGGER.info(f"counting code on: {sources_dir}")  # pylint: disable=W1203

    command = ["cloc", "--sum-one", "--hide-rate"]

    if cloc_params_dict:
        cloc_params_list = []
        for key, val in cloc_params_dict.items():
            cloc_params_list.append(key)
            if val is not None:
                cloc_params_list.append(val)
        command.extend(cloc_params_list)

    if mode == "raw":
        # do nothing
        pass
    elif mode == "json":
        command.append("--json")
    else:
        raise RuntimeError(f"unhandled mode: '{mode}'")

    if os.path.islink(sources_dir):
        command.extend(["--follow-links", sources_dir])
    else:
        command.extend([sources_dir])

    _LOGGER.debug("starting cloc with parameters: %s", command)

    try:
        result = subprocess.run(command, capture_output=True, check=True)  # nosec
    except subprocess.CalledProcessError as exc:
        output = exc.stderr.decode("utf-8")
        _LOGGER.error("cloc error: %s", output)
        raise

    output = result.stdout.decode("utf-8")

    # _LOGGER.info( "cloc output:\n%s", output )

    return parse_cloc_output(output, mode, exclude_languages)


def parse_cloc_file(file_path, ignore=None):
    try:
        content = read_file(file_path)
        return parse_cloc_output(content, "raw", ignore)

    except BaseException:
        _LOGGER.error("error while loading file: %s content:\n%s", file_path, content)
        raise


def parse_cloc_output(content, mode="raw", exclude_languages=None):
    if exclude_languages is None:
        exclude_languages = []

    output = content
    overall_code = 0
    exclude_sum = 0

    if mode == "raw":
        # output = output.splitlines()
        # output = output[1:]
        # output = "\n".join(output)

        overall_code = parse_cloc_raw(output)
        for item in exclude_languages:
            exclude_sum += parse_cloc_raw(output, item)

    elif mode == "json":
        output = json.loads(output)
        overall_code = parse_cloc_json(output)
        for item in exclude_languages:
            exclude_sum += parse_cloc_json(output, item)

    else:
        raise RuntimeError(f"unhandled mode: '{mode}'")

    return overall_code - exclude_sum, output


def parse_cloc_raw(content, language="SUM"):
    # if language == "SUM":
    #     language += ":"

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


def parse_cloc_json(content_dict, language="SUM"):
    lang_dict = content_dict[language]
    return lang_dict["code"]
