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
import os
import signal
from subprocess import Popen, PIPE, TimeoutExpired

import psutil

from exception import ParseException
from model.common import needs_token
from output.terminal import STATUS_RUN, STATUS_OK
from util import duration
from validator.exitcode import ExitCodeValidator
from validator.stream import StreamValidator


class TestStep:
    KEY = 'teststep'
    KEY_NAME = 'name'
    KEY_COMMAND = 'command'
    KEY_EXIT = 'exit'
    KEY_STDOUT = 'stdout'
    KEY_STDERR = 'stderr'
    KEY_FATAL = 'fatal'
    KEY_TIMEOUT = 'timeout'

    def __init__(self, yaml_tree):
        # default values
        self.name = None
        self.command = None
        self.fatal = False
        self.timeout = 0
        self.validators = []

        for key, value in yaml_tree.items():
            if key == self.KEY_NAME:
                self.name = value
            elif key == self.KEY_COMMAND:
                self.command = value
            elif key == self.KEY_EXIT:
                self.validators.append(ExitCodeValidator(value))
            elif key == self.KEY_STDOUT:
                self.validators.append(StreamValidator(value, 'stdout'))
            elif key == self.KEY_STDERR:
                self.validators.append(StreamValidator(value, 'stderr'))
            elif key == self.KEY_FATAL:
                if type(value) is not bool:
                    raise ParseException("%s '%s': error parsing %s (%s) : "
                                         "must be a bool" %
                                         (self.KEY,
                                          self.name,
                                          self.KEY_FATAL,
                                          value))
                self.fatal = value
            elif key == self.KEY_TIMEOUT:
                if type(value) is not int:
                    raise ParseException("%s '%s': error parsing %s (%s) : "
                                         "must be an integer" %
                                         (self.KEY, self.name,
                                          self.KEY_TIMEOUT, value))
                self.fatal = yaml_tree[self.KEY_TIMEOUT]
            else:
                raise ParseException("%s (%s): Unknown token '%s'" % (
                    self.KEY, self.name, key))

        # validate mandatory fields
        needs_token(self.name, self.KEY, self.KEY_NAME, self.name)
        needs_token(self.command, self.KEY, self.KEY_COMMAND, self.name)

    def execute(self):
        stdout = b''
        stderr = b''

        process = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=True)
        try:
            stdout, stderr = process.communicate(timeout=0.5)
        except TimeoutExpired:
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                os.kill(child.pid, signal.SIGKILL)
            os.kill(parent.pid, signal.SIGKILL)

        exitcode = process.wait()

        success = True
        for validator in self.validators:
            if not validator.validate(exitcode,
                                      stdout.decode("utf-8"),
                                      stderr.decode("utf-8")):
                success = False

        return success

    def run(self, testcase, summary):
        start = datetime.datetime.now()

        summary.start_test_step()

        print("%s %s: %s" % (STATUS_RUN, testcase.name, self.name))

        self.execute()

        print("%s %s: %s (%d ms)" %
              (STATUS_OK, testcase.name, self.name, duration(start)))
