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
from validator.base import BaseValidator
from validator.regex_matcher import RegexMatcher


class StreamValidator(BaseValidator):
    def __init__(self, yaml_tree, stream):
        self.stream = stream
        self.validators = []

        if type(yaml_tree) is str:
            self.validators.append(RegexMatcher(yaml_tree))
        elif type(yaml_tree) is list:
            for item in yaml_tree:
                self.validators.append(RegexMatcher(item))
        else:
            raise ParseException("%s must be string or list" % stream)

    def validate(self, exitcode, stdout, stderr):
        stream = ''
        if self.stream == 'stdout':
            stream = stdout
        elif self.stream == 'stderr':
            stream = stderr
        else:
            raise Exception("Invalid stream: %s" % self.stream)

        validation_result = True
        for validator in self.validators:
            result = validator.validate(stream, self.stream)

            # The total validation result is True if each result succeeded.
            # Don't abort on the first failure so we can see other failures
            # in the test output as well.
            validation_result = validation_result and result

        return validation_result