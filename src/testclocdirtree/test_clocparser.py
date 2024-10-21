#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import unittest


from testclocdirtree.data import get_data_path
from clocdirtree.clocparser import parse_cloc_raw
from clocdirtree.io import read_file


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class ClocParserTest(unittest.TestCase):
    def test_parse_cloc_raw(self):
        cloc_output_path = get_data_path("cloc-log.txt")
        cloc_output = read_file(cloc_output_path)

        lines_count, output = parse_cloc_raw(cloc_output)

        self.assertEqual(lines_count, 1058181)

        output_lines = output.splitlines()
        self.assertEqual(len(output_lines), 38)
        self.assertEqual(
            "--------------------------------------------------------------------------------", output_lines[0]
        )
        self.assertEqual(
            "--------------------------------------------------------------------------------", output_lines[-1]
        )
