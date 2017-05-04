package main

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
	"../../util"
	"../../util/infoUtil"
)

func main() {
	repoDirPathPtr := flag.String("repo-dir", "", "Path to the git repository directory of the application")
	flag.Parse()

	if *repoDirPathPtr == "" {
		flag.PrintDefaults()
		os.Exit(1)
	}

	var appInfo infoUtil.AppInfo = infoUtil.ReadAppInfo(*repoDirPathPtr)

	// Step 1:
	//run docker compose service
	var service = "test"
	fmt.Println("Test Step 1: Run docker-compose service:", service)
	util.ExecCmd("/stakater/pipeline-library/stages/run-docker-compose-service.sh -a " + appInfo.Application.Name + " -r " + *repoDirPathPtr + " -s " + service)

	// Add more service runs for integration tests, sonar tests etc
}
