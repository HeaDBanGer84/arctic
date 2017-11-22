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

node {
  // Uses the common library form 'https://github.com/icebear8/pipelineLibrary'
  library identifier: 'common-pipeline-library@stable',
  retriever: modernSCM(github(
    credentialsId: '3bc30eda-c17e-4444-a55b-d81ee0d68981',
    id: '4373d2d2-7662-45a3-b336-94ac3cd4aa1a',
    repoOwner: 'icebear8',
    repository: 'pipelineLibrary',
    traits: [
      [$class: 'org.jenkinsci.plugins.github_branch_source.BranchDiscoveryTrait', strategyId: 1],
      [class: 'org.jenkinsci.plugins.github_branch_source.OriginPullRequestDiscoveryTrait', strategyId: 1],
      [$class: 'org.jenkinsci.plugins.github_branch_source.ForkPullRequestDiscoveryTrait', strategyId: 1, trust: [$class: 'TrustContributors']]]))

  @Library('common-pipeline-library') _

  properties([
    pipelineTriggers([cron('H 15 * * 2')]),
    buildDiscarder(logRotator(
      artifactDaysToKeepStr: '5', artifactNumToKeepStr: '5',
      numToKeepStr: '5', daysToKeepStr: '5'))
  ])

  repositoryUtils.checkoutCurrentBranch {
    stageName = 'Checkout'
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
      stage("Push") {
        parallel dockerImage.setupPushTasks {
          dockerRegistryUser = "${projectSettings.dockerHub.user}"
          buildJobs = projectSettings.dockerJobs
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
