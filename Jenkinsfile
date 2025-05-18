pipeline {
    agent any 

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'  
        DOCKER_IMAGE = 'cithit/colli369'                                   //<-----change this to your MiamiID!
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/seeras-sea/225-lab5-1'     //<-----change this to match this new repository!
        KUBECONFIG = credentials('colli369-225')                           //<-----change this to match your kubernetes credentials (MiamiID-225)! 
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
                sh 'npx htmlhint templates/*.html'
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
                    def kubeConfig = readFile(KUBECONFIG)
                    
                    // Force delete the PV with a timeout
                    sh "echo 'Attempting to delete PersistentVolume...'"
                    sh "kubectl delete pv flask-pv --timeout=30s || true"
                    
                    // If it's still stuck, try force removal with a patch
                    sh """
                    echo 'Checking if PV still exists...'
                    if kubectl get pv flask-pv &>/dev/null; then
                        echo 'PV still exists, attempting force removal...'
                        kubectl patch pv flask-pv -p '{"metadata":{"finalizers":null}}' --type=merge || true
                        kubectl delete pv flask-pv --force --grace-period=0 || true
                    else
                        echo 'PV was successfully deleted'
                    fi
                    """
                    
                    // Wait a moment before proceeding
                    sh "echo 'Waiting before creating new PV...'"
                    sh "sleep 5"
                    
                    // Create new PersistentVolume with correct server IP
                    sh """
                    echo 'Creating new PersistentVolume...'
                    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: flask-pv
  labels:
    type: nfs
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteMany
  nfs:
    path: /srv/nfs/colli369
    server: 10.48.10.138
  persistentVolumeReclaimPolicy: Retain
EOF
                    """
                    
                    // Apply the rest of the deployment
                    sh "echo 'Applying the rest of the deployment...'"
                    sh "kubectl delete --all deployments --namespace=default || true"
                    sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-dev.yaml"
                    sh "kubectl apply -f deployment-dev.yaml"
                    
                    sh "echo 'Deployment complete!'"
                }
            }
        }

        stage('Generate Test Data') {
            steps {
                script {
                    sh "sleep 15" // Wait for pod to be ready
                    def appPod = sh(script: "kubectl get pods -l app=flask -o jsonpath='{.items[0].metadata.name}'", returnStdout: true).trim()
                    sh "kubectl exec ${appPod} -- python3 data-gen.py"
                }
            }
        }

        stage("Run Acceptance Tests") {
            steps {
                script {
                    sh 'docker stop qa-tests || true'
                    sh 'docker rm qa-tests || true'
                    sh 'docker build -t qa-tests -f Dockerfile.test .'
                    sh 'docker run qa-tests'
                }
            }
        }
        
        stage("Run Security Checks") {
            steps {
                sh 'docker pull public.ecr.aws/portswigger/dastardly:latest'
                sh '''
                    docker run --user $(id -u) -v ${WORKSPACE}:${WORKSPACE}:rw \
                    -e BURP_START_URL=http://10.48.10.138 \
                    -e BURP_REPORT_FILE_PATH=${WORKSPACE}/dastardly-report.xml \
                    public.ecr.aws/portswigger/dastardly:latest
                '''
            }
        }
        
        stage('Remove Test Data') {
            steps {
                script {
                    def appPod = sh(script: "kubectl get pods -l app=flask -o jsonpath='{.items[0].metadata.name}'", returnStdout: true).trim()
                    sh "kubectl exec ${appPod} -- python3 data-clear.py"
                }
            }
        }
        
        stage('Deploy to Prod Environment') {
            steps {
                script {
                    sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-prod.yaml"
                    sh "kubectl apply -f deployment-prod.yaml"
                }
            }
        }
         
        stage('Check Kubernetes Cluster') {
            steps {
                script {
                    sh "kubectl get all"
                }
            }
        }
    }

    post {
        always {
            junit testResults: 'dastardly-report.xml', skipPublishingChecks: true
        }
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
