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
# This script reads, increments and updates the build number in the
# app CI info file on each build
#
# Authors: Hazim
#
# Argument 1 (-f, --app-ci-info-file): File path to the app CI info yml file
###############################################################################
import pip
import argparse

# Import ruamel.yaml if not exists
try:
    import ruamel.yaml as yaml
except ImportError:
    pip.main(['install', 'ruamel.yaml'])
    import ruamel.yaml as yaml

argParse = argparse.ArgumentParser()
argParse.add_argument('-f', '--app-ci-info-file', dest='f')

opts = argParse.parse_args()

if not any([opts.f]):
    argParse.print_usage()
    print('Argument `-f` or `--app-ci-info-file` must be specified')
    quit()

appCiInfoFile = open(opts.f)
# Use round trip load and dump to store file with current format and comments
appCiInfo = yaml.round_trip_load(appCiInfoFile)
currentBuildNumber = int(appCiInfo['ci_data']['current_build_number'])
appCiInfoFile.close()

# Write new build number to file
with open(opts.f, 'w') as f:
    newBuildNumber = currentBuildNumber + 1
    appCiInfo['ci_data']['current_build_number'] = newBuildNumber
    yaml.round_trip_dump(appCiInfo, f, default_flow_style=False)
    print("Build Number: {}".format(newBuildNumber))
