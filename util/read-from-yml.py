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
# This script reads the given property from specified yml file. Returns null if not present
#
#
# Authors: Hamza
#
# Argument 1 (-f, --app-ci-info-file): File path to the app CI info yml file
# Argument 2 (-p, --property): Property whose value is to be read
#
# Note: App CI info file is the one which is required by stakater to store CI/CD related data.
###############################################################################

import argparse

# Import ruamel.yaml if not exists
try:
    import ruamel.yaml as yaml
except ImportError:
    import subprocess
    # Install via subprocess in this script to output of installation
    try:
        ruamelImportProc = subprocess.run(["pip3", "install", "--user", "ruamel.yaml"],
                                          shell=True,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, check=True)
        if ruamelImportProc.returncode == 0:
            import ruamel.yaml as yaml
        else:
            exit("Could not Import Package, Return Code: {}".format(ruamelImportProc.returncode))
    except subprocess.CalledProcessError as procException:
        exit("Could not Import package: {}".format(procException.stderr.decode('ascii').rstrip()))


argParse = argparse.ArgumentParser()
argParse.add_argument('-f', '--app-ci-info-file', dest='f')
argParse.add_argument('-p', '--property', dest='p')

opts = argParse.parse_args()

if not any([opts.f]):
    argParse.print_usage()
    print('Argument `-f` or `--app-ci-info-file` must be specified')
    exit(1)

if not any([opts.p]):
    argParse.print_usage()
    print('Argument `-p` or `--property` must be specified')
    exit(1)

# read from app-ci-info.yml
with open(opts.f, 'r') as appCiInfoFile:
    # Use round trip load and dump to store file with current format and comments
    appCiInfo = yaml.round_trip_load(appCiInfoFile)
    prop = opts.p
    parentKeys = prop.split('.')
    temp = appCiInfo
    # Checks if key is available
    for i in range(len(parentKeys)):
        if not (parentKeys[i] in temp):
            print("null")
            exit(0)
        temp = temp[parentKeys[i]]

    print(temp)
