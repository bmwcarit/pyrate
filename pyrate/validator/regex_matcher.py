#
# Copyright (C) 2015 BMW Car IT GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import re

from pyrate.exception import ParseException
from pyrate.output.terminal import print_expectation
from pyrate.util import resolveVariables


class RegexMatcher:
    KEY_CONTAINS = 'contains'
    KEY_NOT_CONTAINS = 'notcontains'

    def __init__(self, yaml_tree):
        self.negate = False
        self.pattern = None

        if type(yaml_tree) is str:
            # treat as 'contains'
            self.pattern = yaml_tree
        elif type(yaml_tree) is dict:
            for key, value in yaml_tree.items():
                if key == self.KEY_CONTAINS:
                    self.negate = False
                    self.pattern = value
                elif key == self.KEY_NOT_CONTAINS:
                    self.negate = True
                    self.pattern = value
                else:
                    raise ParseException("unexpected token '%s'" % key)
        else:
            raise ParseException("stream validator must be string or list")

    def validate(self, stream, type, variables):

        pattern = resolveVariables(self.pattern, variables)

        result = re.search(pattern, stream)

        if self.negate:
            # must not match
            if result is not None:
                # found a match
                print_expectation("%s does not contain" %
                                  type, pattern, stream)
                return False
        else:
            if result is None:
                # found no match but expected one
                print_expectation("%s contains" % type, pattern, stream)
                return False

        return True
