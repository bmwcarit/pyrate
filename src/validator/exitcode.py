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
from output.terminal import print_expectation
from validator.base import BaseValidator


class ExitCodeValidator(BaseValidator):

    def __init__(self, yaml_tree):
        self.code = 0
        self.negate = False

        if type(yaml_tree) not in [str, int]:
            raise ParseException("exit must be str or int (is '%s')" %
                                 type(yaml_tree))
        if type(yaml_tree) is int:
            self.code = yaml_tree
        else:
            if yaml_tree == "SUCCESS":
                self.code = 0
            elif yaml_tree == "FAIL":
                self.code = 0
                self.negate = True
            else:
                # TODO has to be parsed
                self.code = 234234

    def validate(self, exitcode, stdout, stderr):
        valid = exitcode == self.code
        if self.negate:
            valid = not valid

        if not valid:
            prefix = 'not ' if self.negate else ''
            expectation = "%s%s" % (prefix, self.code)
            print_expectation("exit status", expectation, "%d" % exitcode)

        return valid
