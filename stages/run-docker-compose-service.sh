#!/bin/bash

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
# creation of web infrastructure stack on Amazon. Stakater is a collection
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
# Authors: Hazim
#
# This script runs docker-compose service
# The script is written in Shell, and not Go or Python because
# the build image name needs to be exported in the shell session for
# docker-compose to read it
###############################################################################

APP_NAME=""
REPO_DIR=""
SERVICE=""

aOptionFlag=false;
rOptionFlag=false;
sOptionFlag=false;

# Get options from the command line
while getopts ":a:r:s:" OPTION
do
    case $OPTION in
        a)
          if [ ! -z "$OPTARG" ]; then aOptionFlag=true; fi #if not empty string, then set flag true
          APP_NAME=$OPTARG
          ;;
        r)
          if [ ! -z "$OPTARG" ]; then rOptionFlag=true; fi #if not empty string, then set flag true
          REPO_DIR=$OPTARG
          ;;
        s)
          if [ ! -z "$OPTARG" ]; then sOptionFlag=true; fi #if not empty string, then set flag true
          SERVICE=$OPTARG
          # Convert value to lowercase
          SERVICE=`echo "$SERVICE" | sed 's/./\L&/g'`
          ;;
        *)
          echo "Usage: $(basename $0) -a <app name> -r <path to the application's repo directory -s <Name of the service to be started>"
          exit 1
          ;;
    esac
done

if ! $aOptionFlag || ! $rOptionFlag || ! $sOptionFlag;
then
  echo "Usage: $(basename $0) -a <app name> -r <path to the application's repo directory -s <Name of the service to be started>"
  exit 1;
fi

# Variable used in docker-compose file
export BUILD_IMAGE_NAME="${APP_NAME}_build"

docker-compose -f ${REPO_DIR}/docker-compose.yml up ${SERVICE}

# Check Status
CONTAINER_NAME="${BUILD_IMAGE_NAME}-${SERVICE}"
STATUS=$(docker wait "${CONTAINER_NAME}")
if [ "$STATUS" != "0" ]; then
   echo "Docker Compose Service '${SERVICE}' FAILED: $STATUS"
   echo "Remove docker container: "
   docker rm -vf ${CONTAINER_NAME}
   exit 1
else
   echo "Docker Compose Service '${SERVICE}' COMPLETED"
   echo "Remove docker container: "
   docker rm -vf ${CONTAINER_NAME}
   exit 0
fi