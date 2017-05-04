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
	"flag"
	"fmt"
	"os"
	"../util"
	"../util/infoUtil"
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
	var appCiInfo infoUtil.AppCiInfo = infoUtil.ReadAppCiInfo(*repoDirPathPtr, *ciMetadataDirPathPtr)

	fmt.Println("Publish to Docker Register Step 1: Build Docker Image with version:", appCiInfo.CiData.CurrentVersion)

	//TODO: build with version and tag latest
	// TODO: Remove deployment block from app ci info ? or add these build context paths etc ?
	// TODO: update pre reqs txt
	var buildContext = *repoDirPathPtr + "/deployment/publish"
	util.ExecCmd("docker build -t " + appInfo.Application.Name + " -f " + buildContext + "/Dockerfile " + buildContext)

}
