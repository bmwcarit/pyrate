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
from threading import Thread
import time
from subprocess import Popen, PIPE

import psutil

from pyrate.exception import ParseException
from pyrate.model.common import needs_token
from pyrate.output.terminal import STATUS_RUN, STATUS_OK, STATUS_FAILED
from pyrate.util import duration
from pyrate.validator.exitcode import ExitCodeValidator
from pyrate.validator.stream import StreamValidator


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

        self.failed = False
        self.abort_timeout = False
        self.executed = False

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
                self.timeout = yaml_tree[self.KEY_TIMEOUT]
            else:
                raise ParseException("%s (%s): Unknown token '%s'" % (
                    self.KEY, self.name, key))

        # validate mandatory fields
        needs_token(self.name, self.KEY, self.KEY_NAME, self.name)
        needs_token(self.command, self.KEY, self.KEY_COMMAND, self.name)

    def process_timeout(self, process):
        try:
            start = datetime.datetime.now()

            while duration(start) < self.timeout:
                # when abort is signaled there is no need to kill
                # anything anymore
                if self.abort_timeout:
                    return

                time.sleep(0.001)

            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                os.kill(child.pid, signal.SIGKILL)
                os.kill(parent.pid, signal.SIGKILL)
        except:
            pass

    def execute(self, variables):
        command = self.command.format(**variables)

        process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)

        # if a timeout was specified start a thread which kills the process
        # tree if it's still running after the timeout
        kill_thread = None
        if self.timeout > 0:
            self.abort_timeout = False
            kill_thread = Thread(target=self.process_timeout, args=(process,))
            kill_thread.start()

        stdout, stderr = process.communicate()
        exitcode = process.wait()

        # if the timeout thread is still there we have to stop it
        if kill_thread is not None:
            self.abort_timeout = True
            kill_thread.join()

        success = True
        for validator in self.validators:
            if not validator.validate(exitcode,
                                      stdout.decode("utf-8"),
                                      stderr.decode("utf-8"),
                                      variables):
                success = False

        return success

    def run(self, testcase, variables):
        self.executed = True
        start = datetime.datetime.now()

        print("%s %s: %s" % (STATUS_RUN, testcase.name, self.name))

        status = STATUS_OK
        if not self.execute(variables):
            status = STATUS_FAILED
            self.failed = True

        print("%s %s: %s (%d ms)" %
              (status, testcase.name, self.name, duration(start)))

        return not (self.failed and self.fatal)
