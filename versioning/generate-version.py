#!/usr/bin/env python3

###############################################################################
# Copyright 2017 Aurora Solutions
#
#    http://www.aurorasolutions.io
#
# Aurora Solutions is an innovative services and product company at
# the forefront of the software industry, with processes and practices
# involving Domain Driven Design(DDD), Agile methodologies to build
# scalable, secure, reliable and high performance products.
#
# Stakater is an Infrastructure-as-a-Code DevOps solution to automate the
# creation of web infrastructure stack on Amazon. Stakater is a collection
# of Blueprints; where each blueprint is an opinionated, reusable, tested,
# supported, documented, configurable, best-practices definition of a piece
# of infrastructure. Stakater is based on Docker, CoreOS, Terraform, Packer,
# Docker Compose, GoCD, Fleet, ETCD, and much more.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

###############################################################################
# This script generates a version of the format <major>.<minor>.<patch>+<build_number>,
# following the principles of semantic versioning.
#
# The script checks if the given repository has any git tags assign to it. In case the repo already has
# tags assigned, the script will compare the version from the latest assigned tag and the version from
# app info yml file. If the version from the yml file is greater, then that version will be assigned,
# else the version from latest tag with incremented build_number will be assigned.
# The new build number is also saved to the app info yml file.
#
# Authors: Hazim
#
# Argument 1 (-f, --appinfo-file): File path to the app info yml file
# Argument 2 (-d, --repo-dir): Path to the git repository directory for which the version is to be generated
###############################################################################

import pip
import argparse
import subprocess
import re
import os

# Import ruamel.yaml if not exists
try:
    import ruamel.yaml as yaml
except ImportError:
    pip.main(['install', 'ruamel.yaml'])
    import ruamel.yaml as yaml

argParse = argparse.ArgumentParser()
argParse.add_argument('-f', '--appinfo-file', dest='f')
argParse.add_argument('-d', '--repo-dir', dest='d')

opts = argParse.parse_args()

if not any([opts.d]):
    argParse.print_usage()
    print('Argument `-d` or `--repo-dir` must be specified')
    quit()

if not any([opts.f]):
    argParse.print_usage()
    print('Argument `-f` or `--appinfo-file` must be specified')
    quit()

repoDir = opts.d
if not os.path.isdir(repoDir):
    print("Given Repository path does not exist or is not a directory")
    exit(1)
if not os.path.isdir(repoDir + '/.git'):
    print("Given repository directory is not a git repository")
    exit(1)

# read from file
appInfoFile = open(opts.f)
# Use round trip load and dump to store file with current format and comments
appInfo = yaml.round_trip_load(appInfoFile)
currentBuildNumber = int(appInfo['ci_data']['current_build_number'])
appInfoFile.close()

newBuildNumber = currentBuildNumber + 1

appInfoVersion = str(appInfo['version']['major']) + '.' + str(appInfo['version']['minor']) \
                 + '.' + str(appInfo['version']['patch']) + '+' + str(newBuildNumber)

# Identify new Tag
newTag = ""
try:
    describeProc = subprocess.run(['git', '-C', repoDir, 'describe', '--tags', '--abbrev=0'], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, check=True)
    # If tags exist
    if describeProc.returncode == 0:
        # Decode pipe output in ascii and strip tailing whitespace characters
        latestTag = describeProc.stdout.decode('ascii').rstrip()
        versionFormatMatch = re.match(r'[0-9]+.[0-9]+.[0-9]+\+[0-9]+', latestTag)
        if not versionFormatMatch:
            print('The latest tag assigned to the commit is not of the format: "major.minor.patch+build_number"',
                  '\nPlease make sure the latest tag on your git repo is of the given format or the repo does not '
                  'have any tags')
            exit(1)
        # Parse tag of the format major.minor.patch+buildNumber
        latestTagArray = latestTag.split('.')
        latestMajor = int(latestTagArray[0])
        latestMinor = int(latestTagArray[1])
        latestPatch = int(latestTagArray[2].split('+')[0])
        latestBuildNumber = int(latestTagArray[2].split('+')[1])
        isMajorGreater = appInfo['version']['major'] > latestMajor
        isMinorGreater = appInfo['version']['major'] == latestMajor and appInfo['version']['minor'] > latestMinor
        isPatchGreater = appInfo['version']['major'] == latestMajor and appInfo['version']['minor'] == latestMinor \
                         and appInfo['version']['patch'] > latestPatch
        if isMajorGreater or isMinorGreater or isPatchGreater:
            newTag = appInfoVersion
        else:
            newTag = str(latestMajor) + '.' + str(latestMinor) + '.' + str(latestPatch) + '+' + str(newBuildNumber)
# If no git tags exist
except subprocess.CalledProcessError as describeException:
    if str(describeException.stderr.decode('ascii').rstrip()).__contains__("fatal: No names found"):
        newTag = appInfoVersion
    else:
        print("Error Code: {} \nError: {}".format(describeException.returncode,
                                                  describeException.stderr.decode('ascii').rstrip()))
        exit(1)

# Update yml file
with open(opts.f, 'w') as f:
    # Update build number
    appInfo['ci_data']['current_build_number'] = newBuildNumber
    yaml.round_trip_dump(appInfo, f, default_flow_style=False)
    print("New version: {}".format(newTag))
