#!/usr/bin/env groovy

  def uniqId = "jenkins-slave-${UUID.randomUUID().toString()[0..12]}"
  println(uniqId)
  def JOB_NAME = "${env.JOB_NAME}#${env.BUILD_NUMBER}"
  def IMAGE_ID = "";
  timestamps {
  timeout(time: 60, unit: 'MINUTES') {

  podTemplate(
      cloud: "kubernetes",
      label: uniqId,
      envVars: [
          envVar(key: "JOB_NAME", value: JOB_NAME),
      ],
      volumes: [
        hostPathVolume(hostPath: '/var/run/docker.sock', mountPath: '/var/run/docker.sock')
      ]

      containers: [
      containerTemplate(
          name: "builder",
          image: "my-builder-image",
          ttyEnabled: true,
          resourceRequestCpu: "700m",
          resourceRequestMemory: "1024Mi",
          command: "cat"
          securityContext: [
                    privileged: true
          ]
      ),
      ],
      ){ //*/
      node(uniqId) {
              try {
                sh 'env'
                currentBuild.displayName = "${env.BUILD_NUMBER}"
                retry(3) {
                checkout([
                $class: 'GitSCM',
                  branches: [[name: "refs/heads/main"]],
                  browser: [$class: 'Stash', repoUrl: 'git@github.com:tornado67/assessment.git'],
                  doGenerateSubmoduleConfigurations: false,
                  extensions: [
                    [ $class: 'CloneOption',
                      noTags: false,
                      reference: '',
                      shallow: false ],
                    [ $class: 'SubmoduleOption',
                      disableSubmodules: false,
                      parentCredentials: true,
                      recursiveSubmodules: true,
                      reference: '',
                      trackingSubmodules: false ],
                  ],
                  submoduleCfg: [],
                  userRemoteConfigs: [[
                  credentialsId: 'MY_CREDENTIAL_ID',
                  url: 'git@github.com:tornado67/assessment.git'
                  ]]
                ])
                } // retry
                sh "git log -1"
                def GIT_SHA_SHORT = sh(returnStdout: true, script: "git log -1 --format=%h").trim()
                sh "echo git_sha_short = [${GIT_SHA_SHORT}]"
                def GIT_SHA_FULL = sh(returnStdout: true, script: "git log -1 --format=%H").trim()
                sh "echo git_sha_full = [${GIT_SHA_FULL}]"

                currentBuild.displayName = "${BUILD_NUMBER}"

                withCredentials([

                      sshUserPrivateKey(
                          credentialsId: "MY_CREDENTIAL_ID",
                          keyFileVariable: "SSH_KEY_FILE",
                          passphraseVariable: "",
                          usernameVariable: ""),
                      file(
                          credentialsId: "MY_CREDENTIAL_ID",
                          variable: "config"),
                ]) {
                stage('build') {
                   container('builder') {
                       sh "docker build -t my-test-app-tag . "
                   }
                }
                stage('test-deploy') {
                   container('builder') {
                    IMAGE_ID   = sh(returnStdout: true, script: "docker images -q my-test-app-tag").trim()
                    sh("docker run ${IMAGE_ID} -p 8080:8080 -n my-test-container")
                    sh ("curl  http://127.0.0.1:8080/plotwise") // pipeline will fail if curl returns non zero
                    sh ("curl  http://127.0.0.1:8080/world")
                    sh("docker stop my-test-container")
                    sh("docker rm my-test-container")
                  }
                }
                stage ('tag-and-push'){
                    container('builder') {
                       sh "docker tag ${IMAGE_ID} my-push-tag"
                       sh ("docker push") // creds can be provided via  withCredentials or they can be built into the contaier
                    }
                }

                stage ('deploy'){
                  container('builder') { // basic auth can be done using loadBalancers like AWS ELB
                    sh "helm upgrade --install my-app-release my-app-chart --set image=my-push-tag"
                 }
                }
                } //creds
             } catch(err) {
                  currentBuild.result = 'FAILURE'
                  println(err)
             } finally {
                  currentBuild.result = currentBuild.result ?: 'SUCCESS'
             }

      } //node
      } //podtemplate
      } //timeout
      } //timestamps
