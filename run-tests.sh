#!/bin/bash

# Get the Flask service IP
FLASK_IP=$(kubectl get service flask-dev-service -o jsonpath='{.spec.clusterIP}')

echo "Flask service IP: $FLASK_IP"

# Force rebuild the test image
echo "Building test Docker image..."
docker build --no-cache -t qa-tests -f Dockerfile.test .

# Run the tests
echo "Running tests against Flask service at http://$FLASK_IP:5000"
docker run --network=host -e FLASK_URL=http://$FLASK_IP:5000 qa-tests
