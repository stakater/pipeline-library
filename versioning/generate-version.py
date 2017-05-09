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
# This script generates a version of the format <major>.<minor>.<patch>+<build-number>,
# following the principles of semantic versioning.
#
# The script checks if the given repository has any git tags assign to it. In case the repo already has
# tags assigned, the script will compare the version from the latest assigned tag and the version from
# app info yml file. If the version from the yml file is greater, then that version will be assigned,
# else the version from latest tag with incremented build-number will be assigned.
# The new build number is also saved to the app info yml file.
#
# Authors: Hazim
#
# Argument 1 (-f, --app-ci-info-file): File path to the app CI info yml file
# Argument 2 (-d, --repo-dir): Path to the git repository directory for which the version is to be generated
#
# Note: App CI info file is the one which is required by stakater to store CI/CD related data.
# Wheres the app info file is the one which is placed in the user's application repo containing
# details about the repo/project and version to bump
###############################################################################

import argparse
import subprocess
import re
import os

# Import ruamel.yaml if not exists
try:
    import ruamel.yaml as yaml
except ImportError:
    import pip
    pip.main(['install', '--user', 'ruamel.yaml'])
    import ruamel.yaml as yaml

argParse = argparse.ArgumentParser()
argParse.add_argument('-f', '--app-ci-info-file', dest='f')
argParse.add_argument('-d', '--repo-dir', dest='d')

opts = argParse.parse_args()
appInfoFileName = 'app-info.yml'
versionRegex = r'[0-9]+.[0-9]+.[0-9]+\+[0-9]+'

if not any([opts.d]):
    argParse.print_usage()
    exit('Argument `-d` or `--repo-dir` must be specified')

if not any([opts.f]):
    argParse.print_usage()
    exit('Argument `-f` or `--app-ci-info-file` must be specified')

repoDir = opts.d
if not os.path.isdir(repoDir):
    print("Given Repository path does not exist or is not a directory")
    exit(1)
if not os.path.isdir(repoDir + '/.git'):
    exit("Given repository directory is not a git repository")
if not os.path.isfile(repoDir + '/' + appInfoFileName):
    exit('Given repository does not contain a "app-info.yml" file.\n Please make sure you place that file with '
         'version info in the repository directory.')

# Read from app-info.yml
appInfoFile = open(repoDir + '/' + appInfoFileName)
appInfo = yaml.round_trip_load(appInfoFile)
appInfoFile.close()

# read from app-ci-info.yml
appCiInfoFile = open(opts.f)
# Use round trip load and dump to store file with current format and comments
appCiInfo = yaml.round_trip_load(appCiInfoFile)
# Should already be updated by inc-build-number.py
currentBuildNumber = int(appCiInfo['ci-data']['current-build-number'])
appCiInfoFile.close()

appInfoVersion = str(appInfo['version']['major']) + '.' + str(appInfo['version']['minor']) \
                 + '.' + str(appInfo['version']['patch']) + '+' + str(currentBuildNumber)

# Identify new Tag
newTag = ""
try:
    describeProc = subprocess.run(['git', '-C', repoDir, 'describe', '--tags', '--abbrev=0'], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, check=True)
    # If tags exist
    if describeProc.returncode == 0:
        # Decode pipe output in ascii and strip tailing whitespace characters
        latestTag = describeProc.stdout.decode('ascii').rstrip()
        if not re.match(versionRegex, latestTag):
            exit('The latest tag assigned to the commit is not of the format: '
                 '"major.minor.patch+build-number"\n'
                 'Please make sure the latest tag on your git repo is of the given '
                 'format or the repo does not have any tags')
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
            newTag = str(latestMajor) + '.' + str(latestMinor) + '.' + str(latestPatch) + '+' + str(currentBuildNumber)
# If no git tags exist
except subprocess.CalledProcessError as describeException:
    if str(describeException.stderr.decode('ascii').rstrip()).__contains__("fatal: No names found"):
        newTag = appInfoVersion
    else:
        exit("Error Code: {} \nError: {}".format(describeException.returncode,
                                                  describeException.stderr.decode('ascii').rstrip()))

# Update app-ci-info.yml file
with open(opts.f, 'w') as f:
    appCiInfo['ci-data']['current-version'] = newTag
    yaml.round_trip_dump(appCiInfo, f, default_flow_style=False)
    print("New version: {}".format(newTag))
