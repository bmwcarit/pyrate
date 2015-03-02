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

from exception import ParseException


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
