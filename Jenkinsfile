stage('Generate Test Data') {
    steps {
        script {
            sh "sleep 30" // Increased wait time for pod to be ready
            def appPod = sh(script: "kubectl get pods -l app=flask -o jsonpath='{.items[0].metadata.name}'", returnStdout: true).trim()
            
            // Add error handling
            sh """
            if [ -z \"${appPod}\" ]; then
                echo \"No pods found with label app=flask\"
                kubectl get pods
                exit 1
            fi
            
            echo \"Executing data-gen.py in pod ${appPod}\"
            kubectl exec ${appPod} -- python3 data-gen.py || {
                echo \"Failed to execute data-gen.py\"
                kubectl logs ${appPod}
                exit 1
            }
            """
        }
    }
}
