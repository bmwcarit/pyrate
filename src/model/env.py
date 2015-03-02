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

KEY = 'env'


def parse_env(yaml_tree):

    variables = {}

    if type(yaml_tree) is not dict:
        raise ParseException("env must be a dict")

    # make sure the resulting dict is a string -> string mapping
    for key, value in yaml_tree.items():
        variables[str(key)] = str(value)

    return variables
