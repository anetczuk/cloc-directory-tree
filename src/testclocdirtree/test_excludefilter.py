#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import unittest

from clocdirtree.excludefilter import ExcludeItemFilter


class ExcludeItemFilterTest(unittest.TestCase):

    def test_excluded_single(self):
        excluded = ["*/tmp/*"]
        filter_obj = ExcludeItemFilter(excluded)

        is_excluded = filter_obj.excluded("/aaa/bbb/ccc")
        self.assertEqual(False, is_excluded)

        is_excluded = filter_obj.excluded("/aaa/tmp/ccc")
        self.assertEqual(True, is_excluded)

        is_excluded = filter_obj.excluded("/aaa/xxx/ccc")
        self.assertEqual(False, is_excluded)

    def test_excluded_multi(self):
        excluded = ["*/tmp/*", "*/bbb/*"]
        filter_obj = ExcludeItemFilter(excluded)

        is_excluded = filter_obj.excluded("/aaa/bbb/ccc")
        self.assertEqual(True, is_excluded)

        is_excluded = filter_obj.excluded("/aaa/tmp/ccc")
        self.assertEqual(True, is_excluded)

        is_excluded = filter_obj.excluded("/aaa/xxx/ccc")
        self.assertEqual(False, is_excluded)
