#!/bin/bash

# Delete existing PV and PVC
echo "Deleting existing PV and PVC..."
kubectl delete pvc flask-pvc-dev || true
kubectl delete pv flask-pv-dev || true
sleep 10

# Create a temporary PV YAML file with the correct NFS server IP
echo "Creating temporary PV YAML file..."
cat > temp-pv.yaml << EOF
apiVersion: v1
kind: PersistentVolume
metadata:
  name: flask-pv-dev
  labels:
    type: nfs
    environment: dev
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteMany
  nfs:
    path: /srv/nfs/colli369
    server: 10.48.10.140
  persistentVolumeReclaimPolicy: Retain
  storageClassName: ""
EOF

# Apply the temporary PV
echo "Applying temporary PV..."
kubectl apply -f temp-pv.yaml

# Create a temporary PVC YAML file
echo "Creating temporary PVC YAML file..."
cat > temp-pvc.yaml << EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: flask-pvc-dev
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
  storageClassName: ""
  selector:
    matchLabels:
      type: nfs
      environment: dev
EOF

# Apply the temporary PVC
echo "Applying temporary PVC..."
kubectl apply -f temp-pvc.yaml

# Wait for PVC to be bound
echo "Waiting for PVC to be bound..."
kubectl wait --for=condition=Bound pvc/flask-pvc-dev --timeout=60s || true

# Check PV and PVC status
echo "Checking PV status:"
kubectl get pv | grep dev
kubectl describe pv flask-pv-dev

echo "Checking PVC status:"
kubectl get pvc | grep dev
kubectl describe pvc flask-pvc-dev

# Clean up temporary files
echo "Cleaning up temporary files..."
rm -f temp-pv.yaml temp-pvc.yaml

echo "NFS server IP fix complete."
