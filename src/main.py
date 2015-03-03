#!/usr/bin/env python3
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

from __future__ import print_function
import sys
import datetime
import argparse

import yaml

from exception import ParseException
from model import env
from model.testcase import TestCase
from model.teststep import TestStep
from output.terminal import *
from util import duration


__version__ = "0.1"


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="the test specification")
    parser.add_argument("-d", "--dry",
                        help="dry run (only parse the test specification)",
                        action="store_true")
    args = parser.parse_args()

    start = datetime.datetime.now()

    testspec = yaml.safe_load(open(args.file, "r"))

    steps = {}
    cases = []
    variables = {}

    try:
        # first find all shared test steps
        for item in testspec:
            for key, value in item.items():
                if key == TestStep.KEY:
                    new_step = TestStep(value)
                    steps[new_step.name] = new_step

        # now we can parse all test cases
        for item in testspec:
            for key, value in item.items():
                if key == TestCase.KEY:
                    new_case = TestCase(value, steps)
                    cases.append(new_case)
                elif key == TestStep.KEY:
                    pass
                elif key == env.KEY:
                    variables = env.parse_env(value)
                else:
                    raise ParseException("unexpected token '%s'" % key)
    except ParseException as e:
        print("Parse error: %s" % e, file=sys.stderr)
        sys.exit(1)

    # skip remaining stuff when doing a dry run
    if args.dry:
        print("Parsing the test specification succeeded. "
              "Skip tests due to dry run.")
        sys.exit(0)

    for testcase in cases:
        if not testcase.run(variables):
            # break on fatal failure
            break

    # gather some statistics from the test which were run
    cases_executed = [case for case in cases if case.executed]
    cases_failed = [case for case in cases_executed if case.failed]
    steps_executed = [step for case in cases_executed
                      for step in case.steps if step.executed]
    steps_failed = [step for step in steps_executed if step.failed]

    print(STATUS_SEP)
    print("%s %d tests from %d test cases run. (%d ms total" % (
        STATUS_END, len(steps_executed),
        len(cases_executed), duration(start)))

    if len(cases_failed) > 0:
        message_text_cases = "case"
        if len(cases_executed) > 1:
            message_text_cases = "cases"
        print("%s %d out of %d tests (%d of %d %s) failed" %
              (STATUS_FAILED, len(steps_failed), len(steps_executed),
               len(cases_failed), len(cases_executed), message_text_cases))
        print(STATUS_FAILED)

        message_text_cases = "case"
        if len(cases_failed) > 1:
            message_text_cases = "cases"
        print("%s %d failed %s, listed below:" %
              (STATUS_FAILED, len(cases_failed), message_text_cases))

        for testcase in cases_failed:
            print("%s %s" % (STATUS_FAILED, testcase.name))

        sys.exit(1)
    else:
        print(STATUS_PASSED)


if __name__ == "__main__":
    main()
