package infoUtil

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
	"io/ioutil"
	"gopkg.in/yaml.v2"
	"os"
	"log"
)

type AppInfo struct {
	Application application
	Deployment  deployment
}

type application struct {
	Name  string `yaml:"name"`
	Group string `yaml:"group"`
}

type deployment struct {
	BuildOutputPath string `yaml:"build-output-path"`
}

func ReadAppInfo(repoDirPath string) AppInfo {
	// If given path does not exist or is not a directory
	if repoDirInfo, err := os.Stat(repoDirPath); os.IsNotExist(err) || !repoDirInfo.IsDir() {
		log.Fatal("Given Repository path does not exist or is not a directory")
	}

	// If the given directory path does not contain the .git folder
	if gitDirInfo, err := os.Stat(repoDirPath + "/.git"); os.IsNotExist(err) || !gitDirInfo.IsDir() {
		log.Fatal("Given repository directory is not a git repository")
	}

	var appInfo AppInfo
	// Read YML
	var appInfoPath = repoDirPath + "/app-info.yml"
	source, err := ioutil.ReadFile(appInfoPath)
	if err != nil {
		panic(err)
	}
	err = yaml.Unmarshal(source, &appInfo)
	if err != nil {
		panic(err)
	}

	return appInfo
}
