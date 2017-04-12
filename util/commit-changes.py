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
# Authors: Hamza
#
# Argument 1 (-m, --message): Commit Message
# Argument 2 (-f, --files): Files To Commit
# Argument 3 (-d, --repo-dir): Path to the directory of git repo
#
###############################################################################

import argparse
import subprocess
import os
import json

argParse = argparse.ArgumentParser()
argParse.add_argument('-m', '--message', dest='m')
argParse.add_argument('-d', '--repo-dir', dest='d')
argParse.add_argument('-f', '--files', dest='f')

opts = argParse.parse_args()

if not any([opts.f]):
    argParse.print_usage()
    print('Argument `-f` or `--files` must be specified')
    exit(1)

if not any([opts.d]):
    argParse.print_usage()
    print('Argument `-d` or `--repo-dir` must be specified')
    exit(1)

if not any([opts.m]):
    argParse.print_usage()
    print('Argument `-m` or `--message` must be specified')
    exit(1)

repoDir = opts.d
if not os.path.isdir(repoDir):
    print("Given Repository path does not exist or is not a directory")
    exit(1)
if not os.path.isdir(repoDir + '/.git'):
    print("Given repository directory is not a git repository")
    exit(1)
try:
    files=json.loads(opts.f)
except ValueError as ex:
    print("Inavalid File map : " + str(ex))
    exit(1)
try:
    #-C specifies the git directory and __add__ adds second array to first one
    subprocess.run(['git', '-C', repoDir, 'add'].__add__(files), stdout=subprocess.PIPE,stderr=subprocess.PIPE, check=True)
    subprocess.run(['git', '-C', repoDir, 'commit', '-m', opts.m])
    subprocess.run(['git', '-C', repoDir, 'push'])
except subprocess.CalledProcessError as addException:
    print("Error Code: {} \nError: {}".format(addException.returncode,
                                              addException.stderr.decode('ascii').rstrip()))
    exit(1)