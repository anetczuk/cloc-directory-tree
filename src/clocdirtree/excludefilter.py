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


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

_LOGGER = logging.getLogger(__name__)


##
class ExcludeItemFilter:
    def __init__(self, exclude_set=None):
        self.raw_exclude = set(exclude_set)
        for item in self.raw_exclude.copy():
            if len(item) < 1:
                self.raw_exclude.remove(item)

        self.exclude_set = set()
        self.regex_set = set()

        for excl in self.raw_exclude:
            if "*" in excl:
                ## wildcard found
                pattern = excl
                pattern = pattern.replace("*", ".*")
                regex_obj = re.compile(pattern)
                self.regex_set.add(regex_obj)
            else:
                self.exclude_set.add(excl)

    ## is item excluded?
    def excluded(self, item):
        if item in self.exclude_set:
            return True
        for regex in self.regex_set:
            if regex.match(item):
                return True
        return False
