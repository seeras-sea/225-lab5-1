#!/bin/bash

# Delete the existing PersistentVolume
echo "Deleting existing PersistentVolume..."
kubectl delete pv flask-pv

# Wait to ensure deletion completes
echo "Waiting for deletion to complete..."
sleep 5

# Extract just the PV part from the deployment file
echo "Creating new PersistentVolume..."
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

# Apply the rest of the deployment
echo "Applying the rest of the deployment..."
kubectl apply -f deployment-dev.yaml

echo "Deployment complete!"
