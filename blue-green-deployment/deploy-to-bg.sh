#!/usr/bin/env bash

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


AWS_REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|grep region|awk -F\" '{print $4}')
DEPLOY_STATE_KEY=""
APP_NAME=""
ENVIRONMENT=""
DEPLOY_INSTANCE_TYPE="t2.nano" # default value
SSL_CERTIFICATE_ARN="";
IS_ELB_INTERNAL=false;
ACTIVE_ELB_CIDR_BLOCK="\"0.0.0.0/0\""
TEST_ELB_CIDR_BLOCK="\"0.0.0.0/0\""
ENV_STATE_KEY=""

kOptionFlag=false;
aOptionFlag=false;
eOptionFlag=false;
fOptionFlag=false;
# Get options from the command line
while getopts ":k:r:a:e:f:i:n:o:s:t:" OPTION
do
    case $OPTION in
        k)
          DEPLOY_STATE_KEY=$OPTARG
          kOptionFlag=true;
          ;;
        a)
          aOptionFlag=true;
          APP_NAME=$OPTARG
          ;;
        e)
          eOptionFlag=true;
          ENVIRONMENT=$OPTARG
          ;;
        f)
          fOptionFlag=true;
          ENV_STATE_KEY=$OPTARG
          ;;
        i)
          DEPLOY_INSTANCE_TYPE=$OPTARG
          ;;
        n)
          TEST_ELB_CIDR_BLOCK=$OPTARG
          ;;
        o)
          ACTIVE_ELB_CIDR_BLOCK=$OPTARG
          ;;
        s)
          SSL_CERTIFICATE_ARN=$OPTARG
          ;;
        t)
          IS_ELB_INTERNAL=$OPTARG
          ;;
        *)
          echo "Usage: $(basename $0) -k <key for the state file> -a <app-name> -e <environment> -f <tf-state-key> -i <deploy instance type> -o <active elb security group cidr> -n <test elb security group cidr> -s <SSL CERTIFICATE ARN?> -t <IS ELB INTERNAL ? > (optional)"
          exit 1
          ;;
    esac
done

if ! $kOptionFlag || ! $rOptionFlag || ! $aOptionFlag || ! $eOptionFlag;
then
  echo "Usage: $(basename $0) -k <key for the state file> -a <app-name> -e <environment> -f <tf-state-key> -i <deploy instance type> -o <active elb security group cidr> -n <test elb security group cidr> -s <SSL CERTIFICATE ARN?> (optional) -t <IS ELB INTERNAL ? > (optional)"
  exit 1;
fi

##################
# AMI Params
##################
AMI_PARAMS_FILE="/app/${APP_NAME}/${ENVIRONMENT}/cd/vars/${APP_NAME}_${ENVIRONMENT}_ami_params.txt"
# Check ami params file exist
if [ ! -f ${AMI_PARAMS_FILE} ];
then
   echo "Error: [Deploy-to-AMI] AMI parameters file not found";
   exit 1;
fi;

# Read parameter values from file
AMI_ID=`/gocd-data/scripts/read-parameter.sh ${AMI_PARAMS_FILE} AMI_ID`
# Check parameter values not empty
if test -z ${AMI_ID};
then
   echo "Error: Value for AMI ID not defined.";
   exit 1;
fi;
##############################################

# Update blue green deployment group
/app/stakater/pipeline-library/blue-green-deployment/update-bg-deployment-groups.sh ${APP_NAME} ${ENVIRONMENT} ${AMI_ID} ${AWS_REGION} ${DEPLOY_INSTANCE_TYPE} ${DEPLOY_STATE_KEY} "${SSL_CERTIFICATE_ARN}" ${IS_ELB_INTERNAL} ${ENV_STATE_KEY} "${ACTIVE_ELB_CIDR_BLOCK}" "${TEST_ELB_CIDR_BLOCK}" || exit 1