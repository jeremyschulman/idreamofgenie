#   Copyright 2019 Jeremy Schulman, nwkautomaniac@gmail.com
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from setuptools import setup, find_packages

package_version = '0.1.1'
package_name = 'idreamofgenie'


def requirements(filename='requirements.txt'):
    return open(filename.strip()).readlines()


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name=package_name,
    version=package_version,
    description='Toolbox of modules and scripts for pyATS Genie',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Jeremy Schulman',
    packages=find_packages(),
    url='https://github.com/jeremyschulman/idreamofgenie',
    install_requires=requirements(),
    scripts=[
        'bin/find-host'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking'
    ],
)
