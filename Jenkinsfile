#!/usr/bin/env groovy

// Uses the common library form 'https://github.com/icebear8/pipelineLibrary'
library identifier: 'common-pipeline-library@master',
  retriever: modernSCM(github(
    id: '18306726-fec7-4d80-8226-b78a05add4d0',
    credentialsId: '3bc30eda-c17e-4444-a55b-d81ee0d68981',
    repoOwner: 'icebear8',
    repository: 'pipelineLibrary',
    traits: [
      [$class: 'org.jenkinsci.plugins.github_branch_source.BranchDiscoveryTrait', strategyId: 1],
      [$class: 'org.jenkinsci.plugins.github_branch_source.OriginPullRequestDiscoveryTrait', strategyId: 1],
      [$class: 'org.jenkinsci.plugins.github_branch_source.ForkPullRequestDiscoveryTrait', strategyId: 1, trust: [$class: 'TrustContributors']]]))

node {

  def projectSettings = readJSON text: '''{
    "repository": {
      "url": "https://github.com/icebear8/arctic.git",
      "credentials": "3bc30eda-c17e-4444-a55b-d81ee0d68981"
    },
    "dockerHub": {
      "user": "icebear8"
    },
    "dockerJobs": [
      {"imageName": "nginx",        "dockerfilePath": "./nginx" },
      {"imageName": "denonservice", "dockerfilePath": "./denonRemoteControl" },
      {"imageName": "grav",         "dockerfilePath": "./grav" }
    ]
  }'''
  
  def triggers = jobProperties.getJobBuildTriggers{}
  
  properties([
    pipelineTriggers(triggers),
    buildDiscarder(logRotator(
      artifactDaysToKeepStr: '5', artifactNumToKeepStr: '5',
      numToKeepStr: '5', daysToKeepStr: '5'))
  ])

  def branchNameParameter = "*/${buildUtils.getCurrentBuildBranch()}"
  
  repositoryUtils.checkoutBranch {
    stageName = 'Checkout'
    branchName = branchNameParameter
    repoUrl = "${projectSettings.repository.url}"
    repoCredentials = "${projectSettings.repository.credentials}"
  }

  docker.withServer(env.DEFAULT_DOCKER_HOST_CONNECTION, 'default-docker-host-credentials') {
    try {
      stage("Build") {
        parallel dockerImage.setupBuildTasks {
          dockerRegistryUser = "${projectSettings.dockerHub.user}"
          buildJobs = projectSettings.dockerJobs
        }
      }

      docker.withRegistry('https://index.docker.io/v1/', '91159a0f-4ca9-41bf-911d-55e43059097c') {
        stage("Push") {
          parallel dockerImage.setupPushTasks {
            dockerRegistryUser = "${projectSettings.dockerHub.user}"
            buildJobs = projectSettings.dockerJobs
          }
        }
      }
    }
    finally {
      stage("Clean up") {
        parallel dockerImage.setupRemoveTasks {
          dockerRegistryUser = "${projectSettings.dockerHub.user}"
          buildJobs = projectSettings.dockerJobs
        }
      }
    }
  }
}
