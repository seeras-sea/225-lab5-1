stage('Deploy to Dev Environment') {
    steps {
        script {
            def kubeConfig = readFile(KUBECONFIG)
            
            // Apply the deployment
            sh "echo 'Applying the deployment...'"
            sh "kubectl delete --all deployments --namespace=default || true"
            sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-dev.yaml"
            
            // Apply the PV and PVC first
            sh "echo 'Creating PV and PVC...'"
            sh "kubectl apply -f deployment-dev.yaml"
            
            // Check PV and PVC status
            sh "echo 'Checking PV status:'"
            sh "kubectl get pv"
            sh "kubectl describe pv flask-pv"
            
            sh "echo 'Checking PVC status:'"
            sh "kubectl get pvc"
            sh "kubectl describe pvc flask-pvc"
            
            // Wait for PVC to be bound
            sh "echo 'Waiting for PVC to be bound...'"
            sh "kubectl wait --for=condition=Bound pvc/flask-pvc --timeout=60s || true"
            
            sh "echo 'Deployment complete!'"
        }
    }
}

stage('Generate Test Data') {
    steps {
        script {
            // Check if pods are running
            sh "echo 'Checking if pods are running...'"
            def podsRunning = sh(script: "kubectl get pods -l app=flask", returnStdout: true).trim()
            sh "echo 'Pods status: ${podsRunning}'"
            
            // Check for events that might explain why pods aren't running
            sh "echo 'Checking for events:'"
            sh "kubectl get events | tail -n 20"
            
            // Increase wait time for pod to be fully ready
            sh "echo 'Waiting for pod to be ready...'"
            sh "sleep 45"
            
            // Get the pod name with better error handling
            sh "echo 'Getting pod name...'"
            def podCount = sh(script: "kubectl get pods -l app=flask -o json | jq '.items | length'", returnStdout: true).trim()
            sh "echo 'Number of pods found: ${podCount}'"
            
            if (podCount == "0") {
                sh "echo 'ERROR: No pods found with label app=flask'"
                sh "echo 'Checking pod creation issues:'"
                sh "kubectl get events --sort-by=.metadata.creationTimestamp | grep -i error"
                error "No pods found with label app=flask. Deployment failed."
            }
            
            def appPod = sh(script: "kubectl get pods -l app=flask -o jsonpath='{.items[0].metadata.name}'", returnStdout: true).trim()
            sh "echo 'Using pod: ${appPod}'"
            
            // Check pod status
            def podStatus = sh(script: "kubectl get pod ${appPod} -o jsonpath='{.status.phase}'", returnStdout: true).trim()
            sh "echo 'Pod status: ${podStatus}'"
            
            sh """
            if [ \"${podStatus}\" != \"Running\" ]; then
                echo \"ERROR: Pod is not in Running state. Current state: ${podStatus}\"
                kubectl describe pod ${appPod}
                exit 1
            fi
            """
            
            // Check container status
            sh "echo 'Checking container status...'"
            sh "kubectl describe pod ${appPod}"
            
            // List containers in the pod
            def containers = sh(script: "kubectl get pod ${appPod} -o jsonpath='{.spec.containers[*].name}'", returnStdout: true).trim()
            sh "echo 'Containers in pod: ${containers}'"
            
            // Execute the script with the correct container name
            sh "echo 'Executing data-gen.py...'"
            sh "kubectl exec ${appPod} -- ls -la /nfs/"
            sh "kubectl exec ${appPod} -- python3 -V"
            sh "kubectl exec ${appPod} -- python3 data-gen.py || { echo 'Failed to execute data-gen.py'; kubectl logs ${appPod}; exit 1; }"
            
            sh "echo 'Test data generation completed successfully'"
        }
    }
}
