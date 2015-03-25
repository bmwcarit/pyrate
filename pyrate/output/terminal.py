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

from termcolor import colored

STATUS_SEP = colored('[----------]', 'green')
STATUS_END = colored('[==========]', 'green')
STATUS_RUN = colored('[  RUN     ]', 'green')
STATUS_OK = colored('[      OK  ]', 'green')
STATUS_PASSED = colored('[  PASSED  ]', 'green')
STATUS_FAILED = colored('[  FAILED  ]', 'red')


def print_expectation(type, expected, found, command=None):

    if command is not None:
        print(colored("\n\tCommand:", attrs=['bold']))
        print("\t%s\n" % command)

    print(colored("\n\tExpected (%s):" % type, attrs=['bold']))
    for line in expected.splitlines():
        print(colored("\t%s" % line, 'green'))

    print(colored("\n\tGot:", attrs=['bold']))
    for line in found.splitlines():
        print(colored("\t%s" % line, 'red'))
    print()
