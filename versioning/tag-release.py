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
# This script assigns the given version as a tag to the given repo.
# It also creates a release branch of the format 'release-v<version>'
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
argParse.add_argument('-d', '--repo-dir', dest='d')
argParse.add_argument('-f', '--appinfo-file', dest='f')

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

versionRegex = r'[0-9]+.[0-9]+.[0-9]+\+[0-9]+'

appInfoFile = open(opts.f)
appInfo = yaml.round_trip_load(appInfoFile)
appInfoFile.close()

if int(appInfo['ci_data']['current_build_number']) <= 0:
    print('current_build_number has not been updated yet\n',
          'Run "generate-version.py" first to update the current build number')
    exit(1)

version = str(appInfo['version']['major']) + '.' + str(appInfo['version']['minor']) \
          + '.' + str(appInfo['version']['patch']) + '+' + str(appInfo['ci_data']['current_build_number'])

if not re.match(versionRegex, version):
    print('The given version is not of the format: "major.minor.patch+build_number"',
          '\nPlease make sure that the version is of the given format')
    exit(1)

# Make sure the given tag is greater than the already assigned tag
try:
    describeProc = subprocess.run(['git', '-C', repoDir, 'describe', '--tags', '--abbrev=0'], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, check=True)
    # If tags exist
    if describeProc.returncode == 0:
        # Decode pipe output in ascii and strip tailing whitespace characters
        latestTag = describeProc.stdout.decode('ascii').rstrip()
        if not re.match(versionRegex, latestTag):
            print('The latest tag assigned to the commit is not of the format: "major.minor.patch+build_number"',
                  '\nPlease make sure the latest tag on your git repo is of the given format or the repo does not '
                  'have any tags')
            exit(1)
        # Parse latest tag of the format major.minor.patch+buildNumber
        latestTagArray = latestTag.split('.')
        latestMajor = int(latestTagArray[0])
        latestMinor = int(latestTagArray[1])
        latestPatch = int(latestTagArray[2].split('+')[0])
        latestBuildNumber = int(latestTagArray[2].split('+')[1])
        # Parse passed version of the format major.minor.patch+buildNumber
        versionArray = version.split('.')
        versionMajor = int(versionArray[0])
        versionMinor = int(versionArray[1])
        versionPatch = int(versionArray[2].split('+')[0])
        versionBuildNumber = int(versionArray[2].split('+')[1])

        isMajorGreater = versionMajor > latestMajor
        isMinorGreater = versionMajor == latestMajor and versionMinor > latestMinor
        isPatchGreater = versionMajor == latestMajor and versionMinor == latestMinor \
                         and versionPatch > latestPatch
        isBuildNumberGreater = versionMajor == latestMajor and versionMinor == latestMinor \
                               and versionPatch == latestPatch and versionBuildNumber > latestBuildNumber

        if not (isMajorGreater or isMinorGreater or isPatchGreater or isBuildNumberGreater):
            print('The given version is not greater/higher than the version on the latest git tag',
                  'Please Make sure the given version is greater or higher than the version on the latest git tag')
            # exit(1)
# If no git tags exist
except subprocess.CalledProcessError as describeException:
    # If not error for no tags found, then exit and display the error
    if not (str(describeException.stderr.decode('ascii').rstrip()).__contains__("fatal: No names found")):
        print("Error Code: {} \nError: {}".format(describeException.returncode,
                                                  describeException.stderr.decode('ascii').rstrip()))
        exit(1)

# Assign tag to current commit
try:
    tagProc = subprocess.run(['git', '-C', repoDir, 'tag', '-a', version, '-m', 'Release: {}'.format(version)],
                             stderr=subprocess.PIPE, check=True)

    if tagProc.returncode == 0:
        print("Tag {} assigned successfully".format(version))
        branchName = 'release-v' + version
        # try:
        branchProc = subprocess.run(['git', '-C', repoDir, 'branch', branchName, version],
                                    stderr=subprocess.PIPE, check=True)
        if branchProc.returncode == 0:
            pushTagProc = subprocess.run(['git', '-C', repoDir, 'push', 'origin', version],
                                         stderr=subprocess.PIPE, check=True)

            print('Release Branch {} created successfully'.format(branchName))
            pushBranchProc = subprocess.run(['git', '-C', repoDir, 'push', 'origin', branchName],
                                            stderr=subprocess.PIPE, check=True)

            if pushTagProc.returncode == 0 and pushBranchProc.returncode == 0:
                print('Tag {} pushed successfully'.format(version))
                print('Release branch {} pushed successfully'.format(branchName))
                exit(0)

except subprocess.CalledProcessError as procException:
    print('Execution of the following failed: \nCommand: "{}"'.format(procException.cmd, procException.args))
    print(
        'Error Code: {} \nError: "{}"'.format(procException.returncode, procException.stderr.decode('ascii').rstrip()))
    exit(1)
