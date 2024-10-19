#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import unittest

from clocdirtree.graph import generate_graph, split_to_multi_dict, split_to_level_dict


class GraphTest(unittest.TestCase):

    def test_generate_graph(self):
        data_dict = {"aaa": 10, "bbb": 30}
        graph = generate_graph(data_dict)

        graph_data = """\
digraph G {
aaa [color=gray, fixedsize=true, label="aaa\\n10", shape=circle, width=4.618802153517006];
bbb [color=gray, fixedsize=true, label="bbb\\n30", shape=circle, width=8.0];
}
"""
        graph_str = graph.toString()
        self.assertEqual(graph_data, graph_str)

    def test_split_to_multi_dict(self):
        data_dict = {"/aaa/bbb/ccc": 1, "/aaa/ddd": 2, "/aaa": 3, "/aaa/eee": 4}
        split_dict = split_to_multi_dict(data_dict)
        self.assertEqual(
            {"": [None, {"aaa": [3, {"bbb": [None, {"ccc": [1, {}]}], "ddd": [2, {}], "eee": [4, {}]}]}]}, split_dict
        )

    def test_split_to_level_dict(self):
        data_dict = {"/aaa/bbb/ccc": 1, "/aaa/ddd": 2, "/aaa": 3, "/aaa/eee": 4}
        split_dict = split_to_level_dict(data_dict)
        self.assertEqual({2: {"/aaa": 3}, 3: {"/aaa/ddd": 2, "/aaa/eee": 4}, 4: {"/aaa/bbb/ccc": 1}}, split_dict)
