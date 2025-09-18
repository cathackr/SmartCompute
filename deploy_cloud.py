#!/usr/bin/env python3
"""
SmartCompute Cloud Deployment Script
====================================

Script para despliegue automático de SmartCompute Central Server
en diferentes proveedores de nube: Google Cloud, AWS, Azure y nubes privadas.
"""

import os
import json
import yaml
import subprocess
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudDeploymentManager:
    """Gestor de despliegue en la nube"""

    def __init__(self, config_file: str = "deployment_config.yaml"):
        self.config = self._load_deployment_config(config_file)
        self.deployment_files_created = []

    def _load_deployment_config(self, config_file: str) -> Dict[str, Any]:
        """Cargar configuración de despliegue"""
        default_config = {
            'project_name': 'smartcompute-central',
            'version': '1.0.0',
            'environment': 'production',
            'resources': {
                'cpu': '2',
                'memory': '4Gi',
                'storage': '50Gi',
                'replicas': 2
            }
        }

        if Path(config_file).exists():
            with open(config_file, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)

        return default_config

    def create_docker_files(self) -> List[str]:
        """Crear archivos Docker"""
        files_created = []

        # Dockerfile
        dockerfile_content = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    sqlite3 \\
    redis-tools \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs backups certs static

# Expose ports
EXPOSE 8080 8443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["python", "smartcompute_central_server.py"]
"""

        with open('Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        files_created.append('Dockerfile')

        # Docker Compose
        docker_compose_content = f"""
version: '3.8'

services:
  smartcompute-server:
    build: .
    container_name: smartcompute-central
    ports:
      - "8080:8080"
      - "8443:8443"
    environment:
      - ENVIRONMENT={self.config['environment']}
      - DATABASE_PATH=/app/data/smartcompute_central.db
      - REDIS_HOST=redis
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./backups:/app/backups
      - ./certs:/app/certs
    depends_on:
      - redis
    restart: unless-stopped
    networks:
      - smartcompute-network

  redis:
    image: redis:7-alpine
    container_name: smartcompute-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped
    networks:
      - smartcompute-network

  dashboard:
    build: .
    container_name: smartcompute-dashboard
    ports:
      - "8081:8081"
    environment:
      - DATABASE_PATH=/app/data/smartcompute_central.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    command: ["python", "incident_management_dashboard.py"]
    depends_on:
      - smartcompute-server
    restart: unless-stopped
    networks:
      - smartcompute-network

volumes:
  redis_data:

networks:
  smartcompute-network:
    driver: bridge
"""

        with open('docker-compose.yml', 'w') as f:
            f.write(docker_compose_content)
        files_created.append('docker-compose.yml')

        # Requirements.txt
        requirements_content = """
aiohttp==3.9.1
aiofiles==23.2.1
aiohttp-jinja2==1.5.1
cryptography==41.0.7
PyJWT==2.8.0
redis==5.0.1
websockets==12.0
pyyaml==6.0.1
psutil==5.9.6
jinja2==3.1.2
"""

        with open('requirements.txt', 'w') as f:
            f.write(requirements_content)
        files_created.append('requirements.txt')

        logger.info(f"Created Docker files: {', '.join(files_created)}")
        self.deployment_files_created.extend(files_created)
        return files_created

    def create_kubernetes_manifests(self) -> List[str]:
        """Crear manifiestos de Kubernetes"""
        files_created = []
        k8s_dir = Path('k8s')
        k8s_dir.mkdir(exist_ok=True)

        # Namespace
        namespace_manifest = """
apiVersion: v1
kind: Namespace
metadata:
  name: smartcompute
  labels:
    name: smartcompute
"""

        namespace_file = k8s_dir / 'namespace.yaml'
        with open(namespace_file, 'w') as f:
            f.write(namespace_manifest)
        files_created.append(str(namespace_file))

        # ConfigMap
        configmap_manifest = f"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: smartcompute-config
  namespace: smartcompute
data:
  server_config.yaml: |
    server:
      host: "0.0.0.0"
      port: 8080
      ssl_port: 8443
    database:
      path: "/app/data/smartcompute_central.db"
      backup_enabled: true
    redis:
      host: "redis-service"
      port: 6379
    cloud:
      provider: "kubernetes"
    security:
      api_key_required: true
    incident_management:
      auto_escalation: true
"""

        configmap_file = k8s_dir / 'configmap.yaml'
        with open(configmap_file, 'w') as f:
            f.write(configmap_manifest)
        files_created.append(str(configmap_file))

        # Deployment
        deployment_manifest = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smartcompute-server
  namespace: smartcompute
  labels:
    app: smartcompute-server
spec:
  replicas: {self.config['resources']['replicas']}
  selector:
    matchLabels:
      app: smartcompute-server
  template:
    metadata:
      labels:
        app: smartcompute-server
    spec:
      containers:
      - name: smartcompute-server
        image: gcr.io/smartcompute-project/central-server:{self.config['version']}
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 8443
          name: https
        env:
        - name: ENVIRONMENT
          value: "{self.config['environment']}"
        - name: DATABASE_PATH
          value: "/app/data/smartcompute_central.db"
        - name: REDIS_HOST
          value: "redis-service"
        resources:
          requests:
            cpu: "{self.config['resources']['cpu']}"
            memory: "{self.config['resources']['memory']}"
          limits:
            cpu: "{self.config['resources']['cpu']}"
            memory: "{self.config['resources']['memory']}"
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        - name: config-volume
          mountPath: /app/server_config.yaml
          subPath: server_config.yaml
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: smartcompute-pvc
      - name: config-volume
        configMap:
          name: smartcompute-config
"""

        deployment_file = k8s_dir / 'deployment.yaml'
        with open(deployment_file, 'w') as f:
            f.write(deployment_manifest)
        files_created.append(str(deployment_file))

        # Service
        service_manifest = """
apiVersion: v1
kind: Service
metadata:
  name: smartcompute-service
  namespace: smartcompute
spec:
  selector:
    app: smartcompute-server
  ports:
  - name: http
    port: 80
    targetPort: 8080
  - name: https
    port: 443
    targetPort: 8443
  type: LoadBalancer
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: smartcompute
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
"""

        service_file = k8s_dir / 'service.yaml'
        with open(service_file, 'w') as f:
            f.write(service_manifest)
        files_created.append(str(service_file))

        # PersistentVolumeClaim
        pvc_manifest = f"""
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: smartcompute-pvc
  namespace: smartcompute
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: {self.config['resources']['storage']}
  storageClassName: standard
"""

        pvc_file = k8s_dir / 'pvc.yaml'
        with open(pvc_file, 'w') as f:
            f.write(pvc_manifest)
        files_created.append(str(pvc_file))

        # Redis Deployment
        redis_manifest = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: smartcompute
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command: ["redis-server", "--appendonly", "yes"]
        volumeMounts:
        - name: redis-data
          mountPath: /data
      volumes:
      - name: redis-data
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: smartcompute
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
"""

        redis_file = k8s_dir / 'redis.yaml'
        with open(redis_file, 'w') as f:
            f.write(redis_manifest)
        files_created.append(str(redis_file))

        logger.info(f"Created Kubernetes manifests: {len(files_created)} files")
        self.deployment_files_created.extend(files_created)
        return files_created

    def create_terraform_config(self, provider: str) -> List[str]:
        """Crear configuración de Terraform"""
        files_created = []
        terraform_dir = Path('terraform')
        terraform_dir.mkdir(exist_ok=True)

        if provider == 'gcp':
            files_created.extend(self._create_gcp_terraform())
        elif provider == 'aws':
            files_created.extend(self._create_aws_terraform())
        elif provider == 'azure':
            files_created.extend(self._create_azure_terraform())

        self.deployment_files_created.extend(files_created)
        return files_created

    def _create_gcp_terraform(self) -> List[str]:
        """Crear configuración de Terraform para Google Cloud"""
        files_created = []

        # Main Terraform configuration
        main_tf = """
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "smartcompute-terraform-state"
    prefix = "central-server"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# GKE Cluster
resource "google_container_cluster" "smartcompute" {
  name     = "smartcompute-cluster"
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }
}

resource "google_container_node_pool" "smartcompute_nodes" {
  name       = "smartcompute-node-pool"
  location   = var.region
  cluster    = google_container_cluster.smartcompute.name
  node_count = var.node_count

  node_config {
    preemptible  = var.preemptible
    machine_type = var.machine_type

    service_account = google_service_account.smartcompute.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      environment = var.environment
    }

    tags = ["smartcompute", "gke-node"]
  }
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "smartcompute-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "smartcompute-subnet"
  ip_cidr_range = "10.10.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
}

# Service Account
resource "google_service_account" "smartcompute" {
  account_id   = "smartcompute-sa"
  display_name = "SmartCompute Service Account"
}

# Cloud SQL Instance
resource "google_sql_database_instance" "smartcompute_db" {
  name             = "smartcompute-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = var.db_instance_type

    backup_configuration {
      enabled    = true
      start_time = "02:00"
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.self_link
    }
  }

  deletion_protection = true
}

# Cloud Storage Bucket for backups
resource "google_storage_bucket" "backups" {
  name     = "${var.project_id}-smartcompute-backups"
  location = var.region

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 90
    }
  }
}

# Load Balancer
resource "google_compute_global_address" "smartcompute_ip" {
  name = "smartcompute-ip"
}
"""

        main_file = Path('terraform') / 'main.tf'
        with open(main_file, 'w') as f:
            f.write(main_tf)
        files_created.append(str(main_file))

        # Variables
        variables_tf = """
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "node_count" {
  description = "Number of nodes in the node pool"
  type        = number
  default     = 2
}

variable "machine_type" {
  description = "Machine type for nodes"
  type        = string
  default     = "e2-standard-2"
}

variable "preemptible" {
  description = "Use preemptible nodes"
  type        = bool
  default     = false
}

variable "db_instance_type" {
  description = "Database instance type"
  type        = string
  default     = "db-g1-small"
}
"""

        variables_file = Path('terraform') / 'variables.tf'
        with open(variables_file, 'w') as f:
            f.write(variables_tf)
        files_created.append(str(variables_file))

        # Outputs
        outputs_tf = """
output "kubernetes_cluster_name" {
  value       = google_container_cluster.smartcompute.name
  description = "GKE Cluster Name"
}

output "kubernetes_cluster_host" {
  value       = google_container_cluster.smartcompute.endpoint
  description = "GKE Cluster Host"
}

output "load_balancer_ip" {
  value       = google_compute_global_address.smartcompute_ip.address
  description = "Load Balancer IP"
}

output "backup_bucket_name" {
  value       = google_storage_bucket.backups.name
  description = "Backup bucket name"
}
"""

        outputs_file = Path('terraform') / 'outputs.tf'
        with open(outputs_file, 'w') as f:
            f.write(outputs_tf)
        files_created.append(str(outputs_file))

        return files_created

    def _create_aws_terraform(self) -> List[str]:
        """Crear configuración de Terraform para AWS"""
        files_created = []

        # AWS Terraform configuration (simplificado)
        main_tf = """
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "smartcompute-terraform-state"
    key    = "central-server/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.region
}

# EKS Cluster
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "smartcompute-cluster"
  cluster_version = "1.27"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    smartcompute = {
      min_size     = 1
      max_size     = 10
      desired_size = 2

      instance_types = [var.instance_type]
      capacity_type  = "ON_DEMAND"
    }
  }
}

# VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "smartcompute-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.region}a", "${var.region}b", "${var.region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = true

  tags = {
    Environment = var.environment
  }
}

# RDS Database
resource "aws_db_instance" "smartcompute" {
  identifier = "smartcompute-db"

  engine         = "postgres"
  engine_version = "15.3"
  instance_class = var.db_instance_class

  allocated_storage     = 20
  max_allocated_storage = 1000
  storage_type         = "gp2"
  storage_encrypted    = true

  db_name  = "smartcompute"
  username = "smartcompute"
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.smartcompute.name

  backup_retention_period = 7
  backup_window          = "02:00-03:00"
  maintenance_window     = "sun:03:00-sun:04:00"

  skip_final_snapshot = true
}

# S3 Bucket for backups
resource "aws_s3_bucket" "backups" {
  bucket = "${var.project_name}-smartcompute-backups"
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id
  versioning_configuration {
    status = "Enabled"
  }
}
"""

        main_file = Path('terraform') / 'main.tf'
        with open(main_file, 'w') as f:
            f.write(main_tf)
        files_created.append(str(main_file))

        return files_created

    def _create_azure_terraform(self) -> List[str]:
        """Crear configuración de Terraform para Azure"""
        files_created = []

        # Azure Terraform configuration (simplificado)
        main_tf = """
terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  backend "azurerm" {
    resource_group_name  = "smartcompute-terraform"
    storage_account_name = "smartcomputeterraform"
    container_name       = "tfstate"
    key                  = "central-server.terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "smartcompute" {
  name     = "smartcompute-rg"
  location = var.location
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "smartcompute" {
  name                = "smartcompute-aks"
  location            = azurerm_resource_group.smartcompute.location
  resource_group_name = azurerm_resource_group.smartcompute.name
  dns_prefix          = "smartcompute"

  default_node_pool {
    name       = "default"
    node_count = var.node_count
    vm_size    = var.vm_size
  }

  identity {
    type = "SystemAssigned"
  }
}

# PostgreSQL Server
resource "azurerm_postgresql_server" "smartcompute" {
  name                = "smartcompute-psql"
  location            = azurerm_resource_group.smartcompute.location
  resource_group_name = azurerm_resource_group.smartcompute.name

  administrator_login          = "smartcompute"
  administrator_login_password = var.db_password

  sku_name   = var.db_sku_name
  version    = "11"
  storage_mb = 51200

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false
  auto_grow_enabled            = true

  ssl_enforcement_enabled = true
}

# Storage Account for backups
resource "azurerm_storage_account" "backups" {
  name                     = "smartcomputebackups"
  resource_group_name      = azurerm_resource_group.smartcompute.name
  location                 = azurerm_resource_group.smartcompute.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
"""

        main_file = Path('terraform') / 'main.tf'
        with open(main_file, 'w') as f:
            f.write(main_tf)
        files_created.append(str(main_file))

        return files_created

    def create_deployment_scripts(self) -> List[str]:
        """Crear scripts de despliegue"""
        files_created = []

        # Script de despliegue Docker
        docker_deploy_script = """#!/bin/bash
set -e

echo "🚀 Deploying SmartCompute Central Server with Docker"

# Build and start services
docker-compose build
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check health
docker-compose ps
docker-compose logs --tail=50 smartcompute-server

echo "✅ Deployment completed!"
echo "📊 Dashboard: http://localhost:8081"
echo "🔧 API: http://localhost:8080"
"""

        docker_script_file = Path('deploy_docker.sh')
        with open(docker_script_file, 'w') as f:
            f.write(docker_deploy_script)
        docker_script_file.chmod(0o755)
        files_created.append(str(docker_script_file))

        # Script de despliegue Kubernetes
        k8s_deploy_script = """#!/bin/bash
set -e

echo "🚀 Deploying SmartCompute Central Server to Kubernetes"

# Apply manifests
kubectl apply -f k8s/

# Wait for deployment
kubectl -n smartcompute wait --for=condition=available --timeout=300s deployment/smartcompute-server

# Get service information
kubectl -n smartcompute get services
kubectl -n smartcompute get pods

echo "✅ Kubernetes deployment completed!"
echo "🔧 Get external IP: kubectl -n smartcompute get svc smartcompute-service"
"""

        k8s_script_file = Path('deploy_k8s.sh')
        with open(k8s_script_file, 'w') as f:
            f.write(k8s_deploy_script)
        k8s_script_file.chmod(0o755)
        files_created.append(str(k8s_script_file))

        logger.info(f"Created deployment scripts: {', '.join(files_created)}")
        self.deployment_files_created.extend(files_created)
        return files_created

    def generate_ssl_certificates(self):
        """Generar certificados SSL auto-firmados para desarrollo"""
        certs_dir = Path('certs')
        certs_dir.mkdir(exist_ok=True)

        cert_file = certs_dir / 'server.crt'
        key_file = certs_dir / 'server.key'

        if not cert_file.exists() or not key_file.exists():
            logger.info("Generating SSL certificates...")
            subprocess.run([
                'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
                '-keyout', str(key_file),
                '-out', str(cert_file),
                '-days', '365', '-nodes',
                '-subj', '/C=US/ST=CA/L=SF/O=SmartCompute/OU=Security/CN=localhost'
            ], check=True)
            logger.info(f"SSL certificates created: {cert_file}, {key_file}")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='SmartCompute Cloud Deployment Manager')
    parser.add_argument('--provider', choices=['docker', 'k8s', 'gcp', 'aws', 'azure'],
                       default='docker', help='Deployment target')
    parser.add_argument('--config', default='deployment_config.yaml',
                       help='Configuration file')

    args = parser.parse_args()

    deployer = CloudDeploymentManager(args.config)

    logger.info(f"Creating deployment files for: {args.provider}")

    # Generate SSL certificates
    deployer.generate_ssl_certificates()

    # Create common files
    deployer.create_docker_files()

    if args.provider in ['k8s', 'gcp', 'aws', 'azure']:
        deployer.create_kubernetes_manifests()

    if args.provider in ['gcp', 'aws', 'azure']:
        deployer.create_terraform_config(args.provider)

    # Create deployment scripts
    deployer.create_deployment_scripts()

    logger.info("✅ Deployment files created successfully!")
    logger.info("📁 Files created:")
    for file in deployer.deployment_files_created:
        logger.info(f"   - {file}")

    logger.info("\n🚀 Next steps:")
    if args.provider == 'docker':
        logger.info("   - Run: ./deploy_docker.sh")
    elif args.provider == 'k8s':
        logger.info("   - Run: ./deploy_k8s.sh")
    else:
        logger.info(f"   - Configure terraform/{args.provider} variables")
        logger.info("   - Run: cd terraform && terraform init && terraform apply")

if __name__ == "__main__":
    main()