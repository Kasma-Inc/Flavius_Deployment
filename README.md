# Flavius Deployment Guide

<!-- toc -->
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Cluster Setup](#cluster-setup)
- [GitOps Repository](#gitops-repository)
- [Service Installation](#service-installation)
  - [MinIO](#minio)
  - [etcd](#etcd)
  - [Flavius Image Pull Credentials](#flavius-image-pull-credentials)
  - [Modify Cluster CoreDNS for K3D](#modify-cluster-coredns-for-k3d)
  - [Install Flavius Services](#install-flavius-services)
- [Verify Deployment](#verify-deployment)
- [Interacting with Flavius](#interacting-with-flavius)
  - [Via FE Pod Shell](#via-fe-pod-shell)
  - [Via Python SDK](#via-python-sdk)
- [Example Python Script](#example-python-script)
- [Troubleshooting](#troubleshooting)
- [License](#license)
<!-- tocstop -->

## Introduction

This guide walks you through deploying and interacting with the Flavius graph platform on a local k3d Kubernetes cluster. By the end, you'll have MinIO object storage, etcd, and Flavius services running, plus examples of how to query Flavius via its FE shell and Python SDK.

## Prerequisites

- **k3d**: Lightweight Kubernetes in Docker (v5.x)
  ```bash
  curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
  ```
- **kubectl**: Kubernetes CLI (latest stable)
  ```bash
  curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"
  chmod +x kubectl
  sudo mv kubectl /usr/local/bin/
  ```  
- **Helm**: Kubernetes package manager (v3.x)
  ```bash
  curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
  ```
- **Python**: 3.10–3.12 for SDK usage

## Cluster Setup

1. **Create k3d cluster**
   ```bash
   k3d cluster create flavius
   ```

2. **(Optional) Delete cluster**
   ```bash
   k3d cluster delete flavius
   ```

3. **Verify cluster**
   ```bash
   kubectl cluster-info
   ```

## GitOps Repository

Clone the deployment manifests:

```bash
git clone https://github.com/Kasma-Inc/Flavius_Deployment.git
cd Flavius_Deployment
```

## Service Installation

### MinIO

Install MinIO via Helm:

```bash
helm install minio oci://registry-1.docker.io/bitnamicharts/minio \
  --create-namespace --namespace minio \
  --set auth.rootUser=fvadmin --set auth.rootPassword=fvadmin123 \
  --set defaultBuckets=flavius \
  --set service.type=NodePort --set service.nodePorts.api=30900 \
  --set persistence.enabled=true --wait
```

### Etcd

Install single-node etcd:

```bash
helm install etcd ./etcd \
  --create-namespace --namespace etcd \
  --set auth.rbac.create=false --set persistence.enabled=true --wait
```

### Flavius Image Pull Credentials

```bash
kubectl create namespace flavius
kubectl -n flavius create secret docker-registry image-pull-secret \
  --docker-server=registry-intl.cn-hongkong.aliyuncs.com \
  --docker-username="flavius_user@5170390357037810" \
  --docker-password="Kasma2025"
```

### Modify Cluster CoreDNS for K3D

```bash
cd /Flavius_Deployment/tools
kubectl -n kube-system apply -f k3d-coredns-custom.yaml
kubectl rollout restart -n kube-system deployment/coredns
```

### Install Flavius Services

```bash
helm install flavius ./flavius \
  --namespace flavius -f ./flavius/values.yaml --wait
```

## Verify Deployment

Check all Pods:

```bash
kubectl get pods --all-namespaces
```

## Interacting with Flavius

Prerequisites
- Forward port 3000 of the Flavius FE pod in your k3d cluster to your local machine.
- Forward port 30900 of your MinIO service to your local machine.
```bash
 k3d cluster edit flavius --port-add 30000:30000@loadbalancer
 kubectl port-forward -n minio svc/minio 30900:9000
```

### Via FE Pod Shell

```bash
kubectl exec -it fe-0 -n flavius -- /bin/bash
cd frontend/
./shell --host localhost --port 30000
```

Please check more details in the Flavius Official [Doc/shell](https://flavius-docs.kasma.ai/shell/) section. 

### Via Python SDK

**Install SDK and dependencies**
   ```bash
   pip3 install flavius_py310  # flavius_py311 | flavius_py312
   pip3 install minio
   ```

## Example Python Script

See `python_sdk/example.py` for a complete demo illustrating:

- Uploading CSV data to MinIO
- Creating namespaces, graphs, vertex and edge tables
- Importing data with BLOCKING IMPORT
- Executing parameterized queries

## Troubleshooting

- **Installation errors**: Verify network access to Docker registry and PyPI.
- **Port conflicts**: Ensure ports 30000 and 30900 are free on your host.
- **DNS issues**: Reapply CoreDNS config as shown above.

## License

This project is licensed under the **Apache 2.0 License**. See [LICENSE](LICENSE) for details.


