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

import copy
import datetime

from pyrate.exception import ParseException
from pyrate.model.common import needs_token
from pyrate.model.teststep import TestStep
from pyrate.output.terminal import STATUS_SEP
from pyrate.util import duration


def create_step(yaml_tree, name, shared_steps):
    if type(yaml_tree) is str:
        # the step refers to a shared step
        if yaml_tree not in shared_steps:
            raise ParseException(
                "%s '%s': undefined reference to %s '%s'" %
                (TestCase.KEY, name, TestStep.KEY, yaml_tree))
        return shared_steps[yaml_tree]
    elif type(yaml_tree) is dict:
        for key, value in yaml_tree.items():
            if key != TestStep.KEY:
                # check for a shared step with argument
                if key in shared_steps:

                    # The step has to be copied. Otherwise all instances of
                    # this step would have the same set of arguments.
                    step = copy.deepcopy(shared_steps[key])
                    step.parse_args(value)
                    return step

                raise ParseException("%s '%s': unexpected token '%s'" %
                                     (TestCase.KEY, name, key))
            return TestStep(value)
    else:
        raise ParseException("%s '%s': unexpected type %s" %
                             (TestCase.KEY, name, type(yaml_tree)))


class TestCase:

    KEY = 'testcase'
    KEY_NAME = 'name'
    KEY_STEPS = 'steps'

    KEY_FATAL = 'fatal'

    def __init__(self, yaml_tree, shared_steps):
        self.name = None
        self.steps = None
        self.fatal = False

        self.failed = False
        self.executed = False

        for key, value in yaml_tree.items():
            if key == self.KEY_NAME:
                self.name = value
            elif key == self.KEY_STEPS:
                self.steps = []
                for yamlStep in value:
                    self.steps.append(create_step(yamlStep, self.name,
                                                  shared_steps))
            elif key == self.KEY_FATAL:
                if type(value) is not bool:
                    raise ParseException("%s '%s': error parsing %s (%s) : "
                                         "must be a bool" %
                                         (self.KEY,
                                          self.name,
                                          self.KEY_FATAL,
                                          value))
                self.fatal = value
            else:
                raise ParseException("%s (%s): Unknown token '%s'" % (
                    self.KEY, self.name, key))

        needs_token(self.name, self.KEY, self.KEY_NAME, self.name)
        needs_token(self.steps, self.KEY, self.KEY_STEPS, self.name)

    def run(self, variables):
        self.executed = True
        start = datetime.datetime.now()
        print("%s %s" % (STATUS_SEP, self.name))

        for step in self.steps:
            # run returns false if a fatal test step failed
            if not step.run(self, variables):
                break

        print("%s %s : %d tests (%d ms total)\n" %
              (STATUS_SEP, self.name, len(self.steps), duration(start)))

        # check if fatal and at least one failure
        failed = [step for step in self.steps if step.failed]
        self.failed = len(failed)
        return not (self.failed > 0 and self.fatal)
