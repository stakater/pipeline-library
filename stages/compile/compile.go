package main

import (
	"flag"
	"fmt"
	"os"
)

/*###############################################################################
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
###############################################################################*/

/**
 * Authors: Hazim
 */

import (
	"fmt"
	"os"
	"flag"
	"../../util/infoUtil"
	"../../util"
)

func main() {
	repoDirPathPtr := flag.String("repo-dir", "", "Path to the git repository directory of the application")
	ciMetadataDirPathPtr := flag.String("ci-metadata-dir", "", "Path to the app CI metadata folder")

	flag.Parse()

	if *repoDirPathPtr == "" || *ciMetadataDirPathPtr == "" {
		fmt.Println("Both Options Must be specified, Usage:")
		flag.PrintDefaults()
		os.Exit(1)
	}

	var appInfo infoUtil.AppInfo = infoUtil.ReadAppInfo(*repoDirPathPtr)

	var ciInfoFilePath = *ciMetadataDirPathPtr + "/" + appInfo.Application.Name + "/app-ci-info.yml"

	// Step 1:
	// increment build number
	fmt.Println("Compile Step 1: Increment Build Number")
	util.ExecCmd("python3 /stakater/pipeline-library/versioning/inc-build-number.py -f " + ciInfoFilePath)

	fmt.Println("Compile Step 2: Remove previous docker containers/images")
	util.ExecCmd("/stakater/pipeline-library/stages/stop-docker-compose-service.sh -a " + appInfo.Application.Name+ " -r " + *repoDirPathPtr)
	// Step 2:
	//run docker compose service
	var service = "compile"
	fmt.Println("Compile Step 3: Run docker-compose service:", service)
	util.ExecCmd("/stakater/pipeline-library/stages/run-docker-compose-service.sh -a " + appInfo.Application.Name+ " -r " + *repoDirPathPtr + " -s " + service)
}