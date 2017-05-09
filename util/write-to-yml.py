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
# This script writes the given map of properties to the specified api CI info file
#
#
# Authors: Hamza
#
# Argument 1 (-f, --app-ci-info-file): File path to the app CI info yml file
# Argument 2 (-d, --ci-repo-dir): Path to the directory of git CI repo
# Argument 3 (-p, --properties-map): Properties map to save in yml
#
# Note: App CI info file is the one which is required by stakater to store CI/CD related data.
###############################################################################

import pip
import argparse
import json
import os
# Import ruamel.yaml if not exists
try:
    import ruamel.yaml as yaml
except ImportError:
    pip.main(['install', 'ruamel.yaml'])
    import ruamel.yaml as yaml

argParse = argparse.ArgumentParser()
argParse.add_argument('-f', '--app-ci-info-file', dest='f')
argParse.add_argument('-d', '--ci-repo-dir', dest='d')
argParse.add_argument('-p', '--properties-map', dest='p')

opts = argParse.parse_args()

if not any([opts.d]):
    argParse.print_usage()
    print('Argument `-d` or `--ci-repo-dir` must be specified')
    exit(1)

if not any([opts.f]):
    argParse.print_usage()
    print('Argument `-f` or `--app-ci-info-file` must be specified')
    exit(1)

if not any([opts.p]):
    argParse.print_usage()
    print('Argument `-p` or `--properties-map` must be specified')
    exit(1)

repoDir = opts.d
if not os.path.isdir(repoDir):
    print("Given Repository path does not exist or is not a directory")
    exit(1)
if not os.path.isdir(repoDir + '/.git'):
    print("Given repository directory is not a git repository")
    exit(1)
# read from app-ci-info.yml
with open(opts.d + '/' + opts.f, 'r') as appCiInfoFile:
    # Use round trip load and dump to store file with current format and comments
    appCiInfo = yaml.round_trip_load(appCiInfoFile)
    try:
        properties = json.loads(opts.p)
    except ValueError as ex:
        print("Inavalid File map : " + str(ex))
        exit(1)
    # Updates properties
    for prop in properties:
        parentKeys = prop.split('.')
        temp = appCiInfo
        # Adds parent keys if not present
        for i in range(len(parentKeys)-1):
            if not(parentKeys[i] in temp):
                temp[parentKeys[i]] = {}
            temp = temp[parentKeys[i]]
        # Adds value to last key
        temp[parentKeys[len(parentKeys)-1]] = properties[prop]
with open(opts.d + '/' + opts.f, 'w') as appCiInfoFile:
    yaml.round_trip_dump(appCiInfo, appCiInfoFile, default_flow_style=False)