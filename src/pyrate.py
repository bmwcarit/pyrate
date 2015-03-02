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
from model.testcase import TestCase
from model.teststep import TestStep
from output.terminal import *
from util import duration


__version__ = "0.1"


class TestSummary:
    def __init__(self):
        self.failedTestCases = 0
        self.failedTestSteps = 0
        self.testCaseSummaries = []
        self.testCasesRun = 0
        self.testStepsRun = 0

    def start_test_case(self):
        self.testCasesRun += 1

    def start_test_step(self):
        self.testStepsRun += 1


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

    summary = TestSummary()
    for testcase in cases:
        if not testcase.run(summary):
            # break on fatal failure
            break

    print(STATUS_SEP)
    print("%s %d tests from %d test cases run. (%d ms total" % (
        STATUS_END, summary.testStepsRun,
        summary.testCasesRun, duration(start)))

    if summary.failedTestCases > 0:
        print("failed")
    else:
        print(STATUS_PASSED)


if __name__ == "__main__":
    main()
