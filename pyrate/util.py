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

import datetime


def duration(start):
    diff = datetime.datetime.now() - start
    return diff.total_seconds() * 1000


def resolveVariables(string, vars, depth = 0):
    new = string.format_map(DefaultVariableDict(**vars))

    # recursively resolve variables if the string has been changed
    if string == new:
        # nothing changed
        return new

    # limit the depth to 10 in order to inhibit an infinite recursion
    if depth < 10:
        return resolveVariables(new, vars, depth + 1)

    return new


class DefaultVariableDict(dict):
    def __missing__(self, key):
        return '{%s}' % key
