pipeline {
    agent any 

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'  
        DOCKER_IMAGE = 'cithit/colli369'
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/seeras-sea/225-lab5-1'
        KUBECONFIG = credentials('colli369-225')
    }

    stages {
        stage('Code Checkout') {
            steps {
                cleanWs()
                checkout([$class: 'GitSCM', branches: [[name: '*/main']],
                          userRemoteConfigs: [[url: "${GITHUB_URL}"]]])
            }
        }

        stage('Lint HTML') {
            steps {
                sh 'npm install htmlhint --save-dev'
                sh 'npx htmlhint templates/*.html || true'
            }
        }

        stage('Static Code Analysis') {
            steps {
                sh 'pip install pylint'
                sh 'pylint --disable=C0111,C0103,C0303 *.py || true'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}", "-f Dockerfile.build .")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_CREDENTIALS_ID}") {
                        docker.image("${DOCKER_IMAGE}:${IMAGE_TAG}").push()
                    }
                }
            }
        }

        stage('Deploy to Dev Environment') {
            steps {
                script {
                    // Update the image tag in the deployment file
                    sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-dev.yaml"
                    
                    // Delete existing PVC and PV if they exist
                    sh "kubectl delete pvc flask-pvc-dev || true"
                    sh "kubectl delete pv flask-pv-dev || true"
                    sh "sleep 10"
                    
                    // Apply the deployment
                    sh "kubectl apply -f deployment-dev.yaml"
                    
                    // Wait for PVC to be bound
                    sh "kubectl wait --for=condition=Bound pvc/flask-pvc-dev --timeout=60s || true"
                    
                    // Wait for pods to be ready
                    sh "sleep 60"
                }
            }
        }

        stage('Generate Test Data') {
            steps {
                script {
                    def appPod = sh(script: "kubectl get pods -l app=flask,environment=dev -o name", returnStdout: true).trim().replaceAll("pod/", "")
                    sh "kubectl exec ${appPod} -- python3 data-gen.py || true"
                }
            }
        }

        stage("Run Acceptance Tests") {
            steps {
                script {
                    sh 'docker build -t qa-tests -f Dockerfile.test .'
                    sh 'docker run qa-tests'
                }
            }
        }
        
        stage('Remove Test Data') {
            steps {
                script {
                    def appPod = sh(script: "kubectl get pods -l app=flask -o jsonpath='{.items[0].metadata.name}'", returnStdout: true).trim()
                    sh "kubectl exec ${appPod} -- python3 data-clear.py || true"
                }
            }
        }
        
        stage('Deploy to Prod Environment') {
            steps {
                script {
                    // Update the image tag in the deployment file
                    sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-prod.yaml"
                    
                    // Delete existing PVC and PV if they exist
                    sh "kubectl delete pvc flask-pvc-prod || true"
                    sh "kubectl delete pv flask-pv-prod || true"
                    sh "sleep 10"
                    
                    // Apply the deployment
                    sh "kubectl apply -f deployment-prod.yaml"
                    
                    // Wait for pods to be ready
                    sh "sleep 60"
                }
            }
        }
    }

    post {
        success {
            slackSend color: "good", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        unstable {
            slackSend color: "warning", message: "Build Unstable: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        failure {
            slackSend color: "danger", message: "Build Failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
    }
}
