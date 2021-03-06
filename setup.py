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

from setuptools import setup

setup(name='pyrate',
      version='0.1.1',
      description='Shell-based testing framework',
      author='Tobias Henkel',
      author_email='tobias.henkel@bmw-carit.de',
      url='https://github.com/bmwcarit/pyrate',
      packages=['pyrate',
                'pyrate.model',
                'pyrate.output',
                'pyrate.validator'],
      license='Apache2',
      scripts=['tools/pyrate'],
      install_requires=[
          "PyYaml",
          "psutil",
          "termcolor"
      ],
)