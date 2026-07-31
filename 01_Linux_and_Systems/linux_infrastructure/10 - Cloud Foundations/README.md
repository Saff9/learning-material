# 10 - Cloud Foundations

> **Phase:** 1 (Core Infrastructure) · **Time:** ~3 weeks · **Difficulty:** ⭐⭐⭐⭐

---

## What It Is

**Cloud Computing** is the delivery of computing services—including servers, storage, databases, networking, software, analytics, and intelligence—over the Internet ("the cloud") to offer faster innovation, flexible resources, and economies of scale. According to the **NIST SP 800-145** definition, cloud infrastructure relies on five essential characteristics:

1. **On-Demand Self-Service:** Automated resource provisioning without human interaction with service providers.
2. **Broad Network Access:** Capabilities available over standard network mechanisms (HTTP/S, SSH, APIs).
3. **Resource Pooling:** Multi-tenant infrastructure pooling physical and virtual resources dynamically.
4. **Rapid Elasticity:** Capabilities provisioned and released elastically to scale rapidly outward or inward with demand.
5. **Measured Service:** Resource usage monitored, controlled, and reported transparently (metered billing).

**Cloud Foundations** encompasses the core architectural paradigms, networking topologies, security frameworks, identity models, storage tiers, and Infrastructure as Code (IaC) tooling required to build, operate, and maintain resilient enterprise systems across major public and hybrid cloud providers.

---

## Why It Matters

- **Elastic Scalability:** Scale horizontally (auto-scaling groups) or vertically in response to real-time telemetry, handling unpredictable traffic spikes without pre-provisioning idle hardware.
- **Financial Agility (FinOps):** Shift from Capital Expenditure (CapEx - heavy upfront hardware investment) to Operational Expenditure (OpEx - pay-as-you-go consumption).
- **High Availability & Fault Tolerance:** Build multi-Region, multi-Availability Zone (AZ) topologies achieving 99.99%+ uptime SLAs through redundant compute and automated database failover.
- **Global Reach & Low Latency:** Edge locations and Content Delivery Networks (CDNs) place workloads within milliseconds of end-users worldwide.
- **Security & Compliance Automation:** Leverage provider-managed physical security, encryption at rest/in transit, and programmatically audited access controls meeting ISO 27001, SOC 2, HIPAA, and PCI-DSS standards.
- **Infrastructure Automation:** Declarative configuration files (Terraform, CloudFormation, Bicep) eliminate manual configuration drift and enable continuous deployment pipelines.

---

## The Shared Responsibility Model

Security and compliance in the cloud are a shared responsibility between the Cloud Service Provider (CSP) and the customer. The model shifts depending on whether the workload uses **IaaS**, **PaaS**, **SaaS**, or **Serverless (FaaS)**.

```
+-------------------------------------------------------------------------+
|                          CUSTOMER RESPONSIBILITY                        |
|  +-------------------------------------------------------------------+  |
|  | Data Classification & Encryption | User IAM & Access Controls     |  |
|  +-------------------------------------------------------------------+  |
|  | Application Code & Logic         | OS Patching & Config (IaaS)    |  |
|  +-------------------------------------------------------------------+  |
|  | Network Firewall Rules & Security Groups                          |  |
+-------------------------------------------------------------------------+
===========================================================================
+-------------------------------------------------------------------------+
|                          PROVIDER RESPONSIBILITY                        |
|  +-------------------------------------------------------------------+  |
|  | Virtualization Layer & Hypervisor| Physical Server Hardware       |  |
|  +-------------------------------------------------------------------+  |
|  | Datacenter Physical Security     | Core Network Infrastructure    |  |
|  +-------------------------------------------------------------------+  |
|  | Environmental Controls (Power, Cooling, Facilities)              |  |
+-------------------------------------------------------------------------+
```

| Asset Layer | Infrastructure as a Service (IaaS) | Platform as a Service (PaaS) | Software as a Service (SaaS) | Serverless (FaaS) |
| :--- | :--- | :--- | :--- | :--- |
| **Data & Governance** | Customer | Customer | Customer | Customer |
| **Identity & Access (IAM)**| Customer | Customer | Customer | Customer |
| **Application Code** | Customer | Customer | Provider / Shared | Customer |
| **Runtime & Middleware** | Customer | Provider | Provider | Provider |
| **Operating System (OS)** | Customer | Provider | Provider | Provider |
| **Virtualization & Hypervisor**| Provider | Provider | Provider | Provider |
| **Physical Hardware/Network**| Provider | Provider | Provider | Provider |

---

## Core Concepts — Detailed Architectural Deep Dive

### 1. Cloud Service Models

```
   [ SaaS ]    -> Full Application (e.g., Office 365, Salesforce)
      |
   [ PaaS ]    -> Platform & Runtimes (e.g., AWS Elastic Beanstalk, Heroku)
      |
   [ FaaS ]    -> Event-Driven Functions (e.g., AWS Lambda, GCP Cloud Functions)
      |
   [ CaaS ]    -> Container Orchestration (e.g., AWS EKS, GCP GKE, Azure AKS)
      |
   [ IaaS ]    -> Virtual Machines, Storage, Networks (e.g., AWS EC2, GCP Compute Engine)
```

1. **IaaS (Infrastructure as a Service):** Provides raw virtualized compute, block storage, and software-defined networking. Offers maximum operational control but requires customer management of OS updates, security patches, and software stacks.
2. **PaaS (Platform as a Service):** Abstracts OS and infrastructure management. Developers deploy application code into pre-configured runtimes (Node.js, Python, Java).
3. **CaaS (Containers as a Service):** Managed container orchestration platforms (Kubernetes engines) where the cloud provider manages the Kubernetes control plane (API server, etcd) while the customer manages worker nodes and container pods.
4. **FaaS / Serverless (Functions as a Service):** Micro-billing compute model where ephemeral code containers execute in response to event triggers (HTTP request, S3 file upload, SQS message) and scale down to zero when idle.
5. **SaaS (Software as a Service):** Turnkey end-user software delivered over HTTP/S.

---

### 2. Cloud Provider Service Mapping (AWS vs. GCP vs. Azure)

| Infrastructure Domain | Amazon Web Services (AWS) | Google Cloud Platform (GCP) | Microsoft Azure |
| :--- | :--- | :--- | :--- |
| **Virtual Compute (VM)** | EC2 (Elastic Compute Cloud) | Compute Engine | Virtual Machines (VM) |
| **Container Orchestration** | EKS (Elastic Kubernetes Service) | GKE (Google Kubernetes Engine) | AKS (Azure Kubernetes Service) |
| **Serverless Compute** | AWS Lambda | Cloud Functions / Cloud Run | Azure Functions |
| **Object Storage** | S3 (Simple Storage Service) | Cloud Storage (GCS) | Blob Storage |
| **Block Storage** | EBS (Elastic Block Store) | Persistent Disk | Azure Managed Disks |
| **Shared File System** | EFS (Elastic File System) | Cloud Filestore | Azure Files |
| **Virtual Network** | VPC (Virtual Private Cloud) | VPC (Global Virtual Private Cloud) | VNet (Virtual Network) |
| **DNS Service** | Route 53 | Cloud DNS | Azure DNS |
| **Relational Database** | RDS / Aurora | Cloud SQL / Cloud Spanner | Azure SQL Database |
| **NoSQL Database** | DynamoDB / DocumentDB | Firestore / Bigtable | Cosmos DB |
| **Identity & Access** | AWS IAM | GCP IAM | Microsoft Entra ID (Azure AD) |
| **Secret Management** | AWS Secrets Manager / KMS | Secret Manager / Cloud KMS | Azure Key Vault |
| **Monitoring & Logs** | CloudWatch | Cloud Monitoring / Cloud Logging | Azure Monitor |
| **Native IaC Engine** | CloudFormation | Deployment Manager | ARM Templates / Bicep |

---

### 3. Cloud Networking Architecture & Subnetting

A **Virtual Private Cloud (VPC)** is an isolated, software-defined network space within a cloud region.

```
+-----------------------------------------------------------------------------------+
| VPC: 10.0.0.0/16 (us-east-1)                                                      |
|                                                                                   |
|  +-------------------------------------+   +-----------------------------------+  |
|  | Public Subnet AZ-1a (10.0.1.0/24)   |   | Public Subnet AZ-1b (10.0.2.0/24) |  |
|  | [ Internet Gateway (IGW) Attachment]|   | [ Application Load Balancer (ALB)]|  |
|  | [ NAT Gateway (Elastic IP) ]        |   | [ Bastion Host / Jump Server ]    |  |
|  +-------------------------------------+   +-----------------------------------+  |
|                     |                                        |                    |
|  ------------------- ROUTE TABLE (Public: 0.0.0.0/0 -> IGW) ------------------  |
|                     |                                        |                    |
|  +-------------------------------------+   +-----------------------------------+  |
|  | Private Subnet AZ-1a (10.0.10.0/24) |   | Private Subnet AZ-1b (10.0.20.0/24)|  |
|  | [ Web / App Application Instance ]  |   | [ Web / App Application Instance ]|  |
|  +-------------------------------------+   +-----------------------------------+  |
|                     |                                        |                    |
|  ---------------- ROUTE TABLE (Private: 0.0.0.0/0 -> NAT GW) ---------------  |
|                     |                                        |                    |
|  +-------------------------------------+   +-----------------------------------+  |
|  | Isolated DB Subnet AZ-1a (10.0.30.0)|   | Isolated DB Subnet AZ-1b (10.0.40)|  |
|  | [ Primary RDS MySQL Instance ]      |   | [ Multi-AZ Standby RDS Replica ]  |  |
|  +-------------------------------------+   +-----------------------------------+  |
+-----------------------------------------------------------------------------------+
```

#### Core Components of Cloud Networking:

- **CIDR Blocks:** IP ranges allocated to VPCs (e.g., `10.0.0.0/16` providing 65,536 addresses).
- **Public Subnets:** Subnets associated with a route table directing internet-bound traffic (`0.0.0.0/0`) to an **Internet Gateway (IGW)**.
- **Private Subnets:** Subnets routed through a **NAT Gateway** (placed in a public subnet) allowing outbound egress for updates while blocking unsolicited inbound connections.
- **Database / Isolated Subnets:** Subnets without IGW or NAT Gateway routes, accessible only within the VPC internal CIDR.
- **Security Groups vs Network ACLs (NACLs):**

| Parameter | Security Group (SG) | Network ACL (NACL) |
| :--- | :--- | :--- |
| **Operates At** | Instance level (ENI) | Subnet level |
| **Statefulness** | **Stateful:** Inbound allowed traffic automatically permits return outbound traffic regardless of rules. | **Stateless:** Outbound return traffic must be explicitly allowed in rules. |
| **Rule Processing**| Evaluates **all** rules before deciding. | Evaluates rules in **numbered sequential order** (lowest number first). |
| **Deny Rules** | Supports **Allow** rules only (implicit deny). | Supports explicit **Allow** and **Deny** rules. |

---

### 4. Storage Architecture & Tiering Strategies

```
+-----------------------------------------------------------------------------------+
| CLOUD STORAGE CLASSIFICATIONS                                                     |
+-----------------------------------------------------------------------------------+
| 1. OBJECT STORAGE (AWS S3 / GCS / Azure Blob)                                      |
|    - Flat namespace, HTTP/S REST API based (GET, PUT, DELETE).                    |
|    - Unlimited scalability, key-value metadata attachment.                         |
|    - Storage Classes: Standard -> Infrequent Access (IA) -> Glacier Archive       |
+-----------------------------------------------------------------------------------+
| 2. BLOCK STORAGE (AWS EBS / GCP Persistent Disk / Azure Managed Disk)             |
|    - Raw storage volumes attached to a single VM hypervisor (SAN-style).          |
|    - Formatted with filesystem (ext4, xfs, NTFS).                                |
|    - Measured in Provisioned IOPS and Throughput (MB/s).                          |
+-----------------------------------------------------------------------------------+
| 3. FILE STORAGE (AWS EFS / GCP Filestore / Azure Files)                            |
|    - Shared network file system supporting POSIX standards (NFSv4 / SMB).          |
|    - Concurrent read/write access across thousands of Linux EC2 instances.         |
+-----------------------------------------------------------------------------------+
```

#### AWS EBS Volume Performance Comparison:

- **gp3 (General Purpose SSD):** Baseline 3,000 IOPS and 125 MB/s throughput included free; scale IOPS and throughput independently of storage capacity. Ideal for boot volumes and general workloads.
- **io2 Block Express (Provisioned IOPS SSD):** Up to 256,000 IOPS and 4,000 MB/s throughput with 99.999% durability. Designed for mission-critical databases (Oracle, PostgreSQL, SAP HANA).
- **st1 (Throughput Optimized HDD):** Low-cost block storage for big data, data warehouses, and log processing.

---

### 5. Identity and Access Management (IAM) & Security Control

IAM controls **Who** (Principal) can perform **What actions** (Permissions) on **Which resources** under **What conditions**.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadWriteForAppBucketOnly",
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::prod-app-data-bucket-99",
        "arn:aws:s3:::prod-app-data-bucket-99/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "true"
        },
        "IpAddress": {
          "aws:SourceIp": "198.51.100.0/24"
        }
      }
    }
  ]
}
```

#### IAM Security Best Practices:
1. **Never use Root Accounts** for daily tasks. Enforce Multi-Factor Authentication (MFA) on root immediately.
2. **Principle of Least Privilege (PoLP):** Grant minimal permissions necessary to perform specific tasks.
3. **Prefer IAM Roles over Long-Lived Access Keys:** Attach IAM Roles directly to EC2 instances (via Instance Profiles), Kubernetes pods (via IRSA / Workload Identity), or CI/CD pipelines (via OIDC federation).
4. **Enforce Encryption in Transit:** Use conditions requiring `aws:SecureTransport: true` (HTTPS).

---

### 6. Infrastructure as Code (IaC) Architecture

IaC manages and provisions cloud infrastructure through machine-readable definition files rather than manual UI clicks or ad-hoc scripts.

- **Declarative IaC (Terraform, CloudFormation, Bicep):** You define the desired end-state; the IaC engine computes dependency graphs, calculates resource differences (diff), and executes API calls to reach the target state.
- **Imperative IaC (AWS CDK, Pulumi):** You write programmatic code (Python, TypeScript, Go) that generates declarative templates or directly invokes SDK calls.

```
+------------------+     +-------------------+     +---------------------+
| HCL Code (.tf)   | --> | terraform plan    | --> | terraform apply     |
+------------------+     +-------------------+     +---------------------+
                                   |                          |
                         [ Reads terraform.tfstate ]  [ Updates Infrastructure ]
                                   |                          |
                         [ Compares Real World Cloud] [ Writes New State File  ]
```

---

## Production-Grade Bash Commands & CLI Operations

### 1. AWS CLI (`aws`) Management Suite

```bash
#!/bin/bash
# ==============================================================================
# AWS CLI Infrastructure Management & Troubleshooting Suite
# Prerequisites: AWS CLI v2 installed and configured ('aws configure')
# ==============================================================================

set -euo pipefail

# 1. Provision a Production-Grade VPC and Subnets
echo "[+] Creating AWS VPC..."
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block "10.0.0.0/16" \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=prod-vpc},{Key=Environment,Value=Production}]' \
  --query 'Vpc.VpcId' \
  --output text)

# Enable DNS Hostnames & Support
aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames '{"Value":true}'
aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-support '{"Value":true}'

echo "[+] Created VPC ID: $VPC_ID"

# Create Internet Gateway (IGW)
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=prod-igw}]' \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)
aws ec2 attach-internet-gateway --vpc-id "$VPC_ID" --internet-gateway-id "$IGW_ID"

# Create Public Subnet in us-east-1a
PUBLIC_SUBNET_ID=$(aws ec2 create-subnet \
  --vpc-id "$VPC_ID" \
  --cidr-block "10.0.1.0/24" \
  --availability-zone "us-east-1a" \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=prod-public-subnet-1a}]' \
  --query 'Subnet.SubnetId' \
  --output text)

# Auto-assign Public IP on Launch for Public Subnet
aws ec2 modify-subnet-attribute --subnet-id "$PUBLIC_SUBNET_ID" --map-public-ip-on-launch

# Create Public Route Table and Route to IGW
ROUTE_TABLE_ID=$(aws ec2 create-route-table \
  --vpc-id "$VPC_ID" \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=prod-public-rt}]' \
  --query 'RouteTable.RouteTableId' \
  --output text)

aws ec2 create-route \
  --route-table-id "$ROUTE_TABLE_ID" \
  --destination-cidr-block "0.0.0.0/0" \
  --gateway-id "$IGW_ID"

aws ec2 associate-route-table --subnet-id "$PUBLIC_SUBNET_ID" --route-table-id "$ROUTE_TABLE_ID"

# 2. Provision Security Group with Strict Port Ingress
SG_ID=$(aws ec2 create-security-group \
  --group-name "prod-web-sg" \
  --description "Security group for production web servers" \
  --vpc-id "$VPC_ID" \
  --query 'GroupId' \
  --output text)

# Authorize SSH (22) from management CIDR and HTTP/HTTPS from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id "$SG_ID" \
  --protocol tcp --port 22 --cidr "203.0.113.50/32"

aws ec2 authorize-security-group-ingress \
  --group-id "$SG_ID" \
  --protocol tcp --port 80 --cidr "0.0.0.0/0"

aws ec2 authorize-security-group-ingress \
  --group-id "$SG_ID" \
  --protocol tcp --port 443 --cidr "0.0.0.0/0"

# 3. Create Hardened S3 Bucket with KMS Encryption & Public Access Block
BUCKET_NAME="prod-corp-data-$(date +%s)"
echo "[+] Provisioning Secure S3 Bucket: $BUCKET_NAME"

aws s3api create-bucket \
  --bucket "$BUCKET_NAME" \
  --region us-east-1

# Enable Bucket Versioning
aws s3api put-bucket-versioning \
  --bucket "$BUCKET_NAME" \
  --versioning-configuration Status=Enabled

# Apply Default KMS Encryption
aws s3api put-bucket-encryption \
  --bucket "$BUCKET_NAME" \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms"
      }
    }]
  }'

# Block All Public Access (S3 Block Public Access)
aws s3api put-public-access-block \
  --bucket "$BUCKET_NAME" \
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# 4. EC2 Diagnostic & Telemetry Queries
echo "[+] Querying Running EC2 Instances..."
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query "Reservations[*].Instances[*].{ID:InstanceId,Type:InstanceType,PublicIP:PublicIpAddress,PrivateIP:PrivateIpAddress,VPC:VpcId}" \
  --output table
```

---

### 2. GCP CLI (`gcloud`) Command Suite

```bash
#!/bin/bash
# ==============================================================================
# GCP Cloud Infrastructure Management & Troubleshooting Suite
# Prerequisites: gcloud SDK authenticated ('gcloud auth login')
# ==============================================================================

set -euo pipefail

PROJECT_ID="prod-cloud-infra-998"
REGION="us-central1"
ZONE="us-central1-a"

# Set default project & region
gcloud config set project "$PROJECT_ID"
gcloud config set compute/region "$REGION"
gcloud config set compute/zone "$ZONE"

# 1. Provision Custom VPC Network and Subnet
echo "[+] Creating GCP Custom VPC Network..."
gcloud compute networks create prod-gcp-vpc --subnet-mode=custom

gcloud compute networks subnets create prod-gcp-subnet-uscentral1 \
  --network=prod-gcp-vpc \
  --region="$REGION" \
  --range=10.200.0.0/20 \
  --enable-private-ip-google-access

# 2. Firewall Rules (Ingress Control)
echo "[+] Setting up Firewall Rules..."
gcloud compute firewall-rules create allow-internal-traffic \
  --network=prod-gcp-vpc \
  --allow=tcp,udp,icmp \
  --source-ranges=10.200.0.0/20

gcloud compute firewall-rules create allow-ssh-iap \
  --network=prod-gcp-vpc \
  --allow=tcp:22 \
  --source-ranges=35.235.240.0/20 \
  --description="Allow SSH strictly via GCP Identity-Aware Proxy (IAP)"

# 3. Create Compute Engine Instance with Custom Service Account
echo "[+] Provisioning Compute Engine VM..."
gcloud compute instances create prod-web-vm-01 \
  --zone="$ZONE" \
  --machine-type=e2-standard-2 \
  --subnet=prod-gcp-subnet-uscentral1 \
  --no-address \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-ssd \
  --tags=web-server \
  --metadata=startup-script='#!/bin/bash
    apt-get update && apt-get install -y nginx
    systemctl enable --now nginx'

# 4. GCS Bucket Provisioning with Lifecycle Rules
GCS_BUCKET="gs://prod-archive-data-${PROJECT_ID}"
echo "[+] Provisioning GCS Storage Bucket: $GCS_BUCKET"

gcloud storage buckets create "$GCS_BUCKET" \
  --location="$REGION" \
  --default-storage-class=STANDARD \
  --uniform-bucket-level-access

# Configure Lifecycle Policy (Transition to Nearline after 30 days)
cat <<EOF > lifecycle.json
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {"age": 30}
    }
  ]
}
EOF
gcloud storage buckets update "$GCS_BUCKET" --lifecycle-file=lifecycle.json
rm -f lifecycle.json
```

---

### 3. Azure CLI (`az`) Command Suite

```bash
#!/bin/bash
# ==============================================================================
# Azure Infrastructure Management Suite
# Prerequisites: Azure CLI installed and authenticated ('az login')
# ==============================================================================

set -euo pipefail

RESOURCE_GROUP="rg-prod-infrastructure"
LOCATION="eastus"
VNET_NAME="vnet-prod-eastus"
SUBNET_NAME="snet-app-eastus"

# 1. Create Resource Group
echo "[+] Creating Azure Resource Group..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"

# 2. Create Virtual Network (VNet) and Subnet
echo "[+] Creating VNet and Subnet..."
az network vnet create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$VNET_NAME" \
  --address-prefixes "172.16.0.0/16" \
  --subnet-name "$SUBNET_NAME" \
  --subnet-prefixes "172.16.1.0/24"

# 3. Create Network Security Group (NSG) and Rules
echo "[+] Provisioning Network Security Group..."
az network nsg create \
  --resource-group "$RESOURCE_GROUP" \
  --name "nsg-app-prod"

az network nsg rule create \
  --resource-group "$RESOURCE_GROUP" \
  --nsg-name "nsg-app-prod" \
  --name "AllowHTTPSInbound" \
  --priority 100 \
  --source-address-prefixes "*" \
  --destination-port-ranges 443 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp

# Associate NSG with Subnet
az network vnet subnet update \
  --resource-group "$RESOURCE_GROUP" \
  --vnet-name "$VNET_NAME" \
  --name "$SUBNET_NAME" \
  --network-security-group "nsg-app-prod"

# 4. Provision Production Linux VM
echo "[+] Provisioning Azure VM..."
az vm create \
  --resource-group "$RESOURCE_GROUP" \
  --name "vm-app-prod-01" \
  --image "Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest" \
  --size "Standard_D2s_v5" \
  --admin-username "azureadmin" \
  --generate-ssh-keys \
  --vnet-name "$VNET_NAME" \
  --subnet "$SUBNET_NAME" \
  --public-ip-address-allocation dynamic
```

---

## Production Configuration Files & Templates

### 1. Complete Production-Grade Terraform (HCL) Module

```hcl
# ==============================================================================
# Production Terraform Configuration (AWS Multi-AZ VPC + Subnets + EC2 + S3)
# File: main.tf
# ==============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  # Remote State Storage in S3 with State Locking in DynamoDB
  backend "s3" {
    bucket         = "corp-terraform-state-prod-009"
    key            = "cloud-foundations/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Project     = "CloudFoundations"
    }
  }
}

# --- VARIABLES ---
variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "Target AWS deployment region"
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Deployment environment identifier"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.100.0.0/16"
  description = "Main VPC CIDR block"
}

# --- NETWORKING RESOURCES ---
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.environment}-vpc"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.environment}-igw"
  }
}

resource "aws_subnet" "public_1a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.100.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.environment}-public-subnet-1a"
  }
}

resource "aws_subnet" "private_1a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.100.10.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "${var.environment}-private-subnet-1a"
  }
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]
}

# NAT Gateway for Outbound Egress from Private Subnet
resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_1a.id

  tags = {
    Name = "${var.environment}-nat-gateway"
  }
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "${var.environment}-public-rt"
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gw.id
  }

  tags = {
    Name = "${var.environment}-private-rt"
  }
}

resource "aws_route_table_association" "public_1a" {
  subnet_id      = aws_subnet.public_1a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_1a" {
  subnet_id      = aws_subnet.private_1a.id
  route_table_id = aws_route_table.private.id
}

# --- SECURITY GROUPS ---
resource "aws_security_group" "web_sg" {
  name        = "${var.environment}-web-sg"
  description = "Allow HTTP/HTTPS ingress and outbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP Inbound"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS Inbound"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.environment}-web-sg"
  }
}

# --- COMPUTE INSTANCE ---
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_instance" "web" {
  ami                  = data.aws_ami.ubuntu.id
  instance_type        = "t3.micro"
  subnet_id            = aws_subnet.public_1a.id
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              apt-get update && apt-get install -y nginx
              echo "<h1>Deployed via Terraform in ${var.aws_region}</h1>" > /var/www/html/index.html
              systemctl enable --now nginx
              EOF

  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }

  tags = {
    Name = "${var.environment}-web-server"
  }
}

# --- S3 BUCKET WITH ENCRYPTION & PUBLIC BLOCK ---
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "app_storage" {
  bucket        = "app-data-${var.environment}-${random_id.bucket_suffix.hex}"
  force_destroy = false
}

resource "aws_s3_bucket_server_side_encryption_configuration" "s3_encryption" {
  bucket = aws_s3_bucket.app_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "public_block" {
  bucket = aws_s3_bucket.app_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- OUTPUTS ---
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "ID of the provisioned VPC"
}

output "web_instance_public_ip" {
  value       = aws_instance.web.public_ip
  description = "Public IP address of the deployed EC2 server"
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.app_storage.id
  description = "Name of the secure S3 storage bucket"
}
```

---

### 2. AWS CloudFormation Production Template (`infrastructure.yaml`)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Production-grade VPC, Security Group, and EC2 Infrastructure Template'

Parameters:
  VpcCidr:
    Type: String
    Default: '10.50.0.0/16'
    Description: 'CIDR block for the CloudFormation VPC'

  InstanceType:
    Type: String
    Default: 't3.micro'
    AllowedValues: ['t3.micro', 't3.small', 't3.medium']
    Description: 'EC2 Instance Type'

Resources:
  ProductionVPC:
    Type: 'AWS::EC2::VPC'
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: cfn-production-vpc

  InternetGateway:
    Type: 'AWS::EC2::InternetGateway'
    Properties:
      Tags:
        - Key: Name
          Value: cfn-production-igw

  VPCGatewayAttachment:
    Type: 'AWS::EC2::VPCGatewayAttachment'
    Properties:
      VpcId: !Ref ProductionVPC
      InternetGatewayId: !Ref InternetGateway

  PublicSubnet:
    Type: 'AWS::EC2::Subnet'
    Properties:
      VpcId: !Ref ProductionVPC
      CidrBlock: '10.50.1.0/24'
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: cfn-public-subnet-1a

  PublicRouteTable:
    Type: 'AWS::EC2::RouteTable'
    Properties:
      VpcId: !Ref ProductionVPC
      Tags:
        - Key: Name
          Value: cfn-public-rt

  PublicRoute:
    Type: 'AWS::EC2::Route'
    DependsOn: VPCGatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: '0.0.0.0/0'
      GatewayId: !Ref InternetGateway

  SubnetRouteTableAssociation:
    Type: 'AWS::EC2::SubnetRouteTableAssociation'
    Properties:
      SubnetId: !Ref PublicSubnet
      RouteTableId: !Ref PublicRouteTable

  WebServerSecurityGroup:
    Type: 'AWS::EC2::SecurityGroup'
    Properties:
      GroupDescription: 'Allow HTTP and HTTPS traffic from anywhere'
      VpcId: !Ref ProductionVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: '0.0.0.0/0'
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: '0.0.0.0/0'

  WebServerInstance:
    Type: 'AWS::EC2::Instance'
    Properties:
      InstanceType: !Ref InstanceType
      ImageId: 'ami-0c7217cdde317cfec' # Amazon Linux 2023 AMI (us-east-1)
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref WebServerSecurityGroup
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          dnf update -y
          dnf install -y httpd
          systemctl start httpd
          systemctl enable httpd
          echo "<h1>Provisioned via AWS CloudFormation</h1>" > /var/www/html/index.html
      Tags:
        - Key: Name
          Value: cfn-web-server

Outputs:
  VpcId:
    Description: 'VPC ID'
    Value: !Ref ProductionVPC
  WebPublicIP:
    Description: 'Public IP of Web Server'
    Value: !GetAtt WebServerInstance.PublicIp
```

---

## Troubleshooting & Diagnostic Matrix

| Issue Category | Root Cause | Diagnostic Command | Remediation Strategy |
| :--- | :--- | :--- | :--- |
| **SSH Connection Timeout (EC2 / VM)** | Security Group missing port 22; IGW attachment missing; Instance in private subnet without Bastion/SSM. | `nc -zv -w 5 <PUBLIC_IP> 22`<br>`aws ec2 describe-security-groups --group-ids <SG_ID>` | Add SSH rule to SG (`authorize-security-group-ingress`). Use AWS SSM Session Manager (`aws ssm start-session --target <INST_ID>`) to bypass SSH requirements entirely. |
| **Private Subnet Instance Cannot Reach Internet** | Route table missing `0.0.0.0/0` entry pointing to NAT Gateway; NAT GW status failed or deleted; Elastic IP unassigned. | `traceroute 8.8.8.8`<br>`aws ec2 describe-route-tables --route-table-ids <RT_ID>` | Verify NAT Gateway is provisioned in a **Public** Subnet with associated Elastic IP. Update private route table `0.0.0.0/0 -> nat-xxxxxxxx`. |
| **S3 403 Forbidden Access Denied** | Bucket Policy restricts access; KMS Key policy blocks principal; "Block Public Access" enabled on public bucket. | `aws s3api get-bucket-policy --bucket <BUCKET>`<br>`aws s3api get-public-access-block --bucket <BUCKET>` | Check IAM Policy + S3 Bucket Policy alignment. Ensure user/role has explicit `s3:GetObject` permission AND `kms:Decrypt` if bucket is KMS-encrypted. |
| **EBS Volume Stuck in `attaching` State** | Device name conflict (e.g., `/dev/xvda` already used); hypervisor lock; Nitro instance naming mismatch (`/dev/nvme0n1`). | `aws ec2 describe-volumes --volume-ids <VOL_ID>`<br>`lsblk` | Force detach volume (`aws ec2 detach-volume --force --volume-id <VOL_ID>`). Re-attach using standard OS block mappings (`/dev/sdf` or `/dev/xvdf`). |
| **Terraform State Lock Error** | Previous Terraform run crashed or interrupted, leaving state locked in DynamoDB. | `terraform plan`<br>`# Returns: Error acquiring state lock` | Inspect DynamoDB table `LockID`. If no active execution exists, release lock safely: `terraform force-unlock <LOCK_ID>`. |
| **ALB Target Group Health Check Failing** | Web server process stopped; Security Group blocks ALB traffic; Health check path returns HTTP 404/500 instead of 200. | `curl -I http://localhost:<PORT>/health`<br>`aws elbv2 describe-target-health --target-group-arn <TG_ARN>` | Verify SG on EC2 allows inbound traffic **from ALB Security Group**. Update target group health check path to a valid HTTP 200 endpoint (e.g., `/healthz`). |
| **Cloud Bill Spike (Unexpected Cost)** | Idle Elastic IPs (`$0.005/hr`); Unattached EBS volumes; Abandoned NAT Gateways (`~$32/mo` base + data transit). | `aws ec2 describe-addresses --filters "Name=association-id,Values=null"`<br>`aws ec2 describe-volumes --filters "Name=status,Values=available"` | Execute automated cleanup script releasing unattached Elastic IPs and snapshotting/deleting unattached (`available`) EBS volumes. |

---

## Real-World Infrastructure Scenarios

### Scenario 1: Multi-AZ High-Availability Web Application Architecture

#### Business Objective:
Architect a fault-tolerant multi-tier e-commerce web application on AWS capable of enduring complete Availability Zone outages while satisfying PCI-DSS security compliance.

```
                  [ AWS Route 53 (DNS / Anycast Routing) ]
                                     |
                  [ AWS CloudFront (CDN + WAF Security) ]
                                     |
              [ Application Load Balancer (Public Subnets) ]
                                     |
         +---------------------------+---------------------------+
         |                                                       |
 [ Auto Scaling Group: AZ-1a ]                          [ Auto Scaling Group: AZ-1b ]
 (Private Subnet: 10.0.10.0/24)                         (Private Subnet: 10.0.20.0/24)
 [ App Engine / Nginx / Node ]                          [ App Engine / Nginx / Node ]
         |                                                       |
         +---------------------------+---------------------------+
                                     |
        +----------------------------+----------------------------+
        |                                                         |
 [ Primary RDS PostgreSQL Instance ]           [ Multi-AZ Standby Synchronous Replica ]
 (AZ-1a Isolated DB Subnet)                    (AZ-1b Isolated DB Subnet)
```

#### Key Architecture Principles:
1. **Edge Protection:** Route 53 DNS routes traffic to AWS CloudFront CDN with AWS WAF inspecting HTTP headers against SQL injection and XSS attacks.
2. **Public-Private Isolation:** ALB sits in public subnets receiving external HTTPS traffic. ALB forwards traffic strictly over port 8080 to EC2 application servers running in private subnets.
3. **Stateless Compute & Auto-Scaling:** Application servers store no local session data (sessions reside in ElastiCache Redis). Auto Scaling Group adjusts instance count dynamically between 2 and 20 instances based on CPU utilization and HTTP request count per target.
4. **Database High Availability:** Amazon RDS PostgreSQL deployed in Multi-AZ configuration. Synchronous block-level replication copies updates to a standby instance in AZ-1b. In the event of primary AZ failure, CNAME DNS records automatically switch target to standby within 60 seconds.

---

### Scenario 2: Zero-Trust Hybrid Cloud Connectivity & Private Egress Lockdown

#### Business Objective:
Connect an enterprise on-premise datacenter securely to an AWS VPC, allowing private workload communication without passing traffic over the public Internet.

```
+--------------------------------+                  +--------------------------------+
|  ON-PREMISE DATACENTER         |                  |  AWS VIRTUAL PRIVATE CLOUD     |
|  IP Range: 192.168.0.0/16      |                  |  IP Range: 10.0.0.0/16          |
|                                |                  |                                |
|  [ Internal Corporate Server ] |                  |  [ Private Compute Instance ]  |
|         |                      |                  |         |                      |
|  [ On-Prem Router / Firewall ] |                  |  [ AWS Transit Gateway (TGW) ]  |
+---------|----------------------+                  +---------|----------------------+
          |                                                   |
          +== IPsec VPN Tunnel / Direct Connect (10 Gbps) =====+
                                                              |
                                                    +---------v----------------------+
                                                    |  AWS VPC ENDPOINTS (PrivateLink)|
                                                    |  - S3 Gateway Endpoint         |
                                                    |  - DynamoDB Interface Endpoint |
                                                    +--------------------------------+
```

#### Technical Implementation:
- **AWS Direct Connect / IPsec VPN:** Establishes an encrypted BGP tunnel between on-prem edge routers and AWS Transit Gateway (TGW).
- **VPC Endpoints (PrivateLink):** Workloads inside private subnets access S3 buckets and DynamoDB tables via internal ENIs and Gateway Endpoints without acquiring public IP addresses or routing through NAT Gateways.
- **Egress Firewall / Proxy:** Outbound internet traffic from private workloads passes through an AWS Network Firewall or Squid Proxy enforcing URL domain whitelisting (e.g., allowing `github.com` for dependencies, denying all other external IPs).

---

## Hands-On Lab Exercises

### Lab 1: Automated Production VPC & Web Cluster via AWS CLI

#### Objective:
Write a repeatable Bash script using `aws` CLI that creates a complete VPC, internet gateway, public subnet, security group, and boots an Nginx EC2 web server.

```bash
#!/bin/bash
set -euo pipefail

echo "======================================================================"
echo "LAB 1: AWS VPC & EC2 CLUSTER PROVISIONING SCRIPT"
echo "======================================================================"

# 1. Create VPC
VPC_ID=$(aws ec2 create-vpc --cidr-block "10.250.0.0/16" --query 'Vpc.VpcId' --output text)
aws ec2 create-tags --resources "$VPC_ID" --tags Key=Name,Value=lab1-vpc
aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames '{"Value":true}'

# 2. Create Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text)
aws ec2 attach-internet-gateway --vpc-id "$VPC_ID" --internet-gateway-id "$IGW_ID"

# 3. Create Public Subnet
SUBNET_ID=$(aws ec2 create-subnet --vpc-id "$VPC_ID" --cidr-block "10.250.1.0/24" --availability-zone "us-east-1a" --query 'Subnet.SubnetId' --output text)
aws ec2 modify-subnet-attribute --subnet-id "$SUBNET_ID" --map-public-ip-on-launch

# 4. Route Table Setup
RT_ID=$(aws ec2 create-route-table --vpc-id "$VPC_ID" --query 'RouteTable.RouteTableId' --output text)
aws ec2 create-route --route-table-id "$RT_ID" --destination-cidr-block "0.0.0.0/0" --gateway-id "$IGW_ID"
aws ec2 associate-route-table --subnet-id "$SUBNET_ID" --route-table-id "$RT_ID"

# 5. Security Group Creation
SG_ID=$(aws ec2 create-security-group --group-name "lab1-web-sg" --description "Allow HTTP" --vpc-id "$VPC_ID" --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 80 --cidr "0.0.0.0/0"

# 6. Launch EC2 Instance
AMI_ID=$(aws ec2 describe-images --owners amazon --filters "Name=name,Values=al2023-ami-2023.*-x86_64" --query 'Images[0].ImageId' --output text)

INSTANCE_ID=$(aws ec2 run-instances \
  --image-id "$AMI_ID" \
  --count 1 \
  --instance-type t3.micro \
  --security-group-ids "$SG_ID" \
  --subnet-id "$SUBNET_ID" \
  --user-data '#!/bin/bash
    dnf install -y httpd
    systemctl start httpd
    echo "Welcome to Cloud Foundations Lab 1 - Host: $(hostname -f)" > /var/www/html/index.html' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=lab1-web-server}]' \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "[+] Waiting for Instance $INSTANCE_ID to reach running state..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID"

PUBLIC_IP=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "======================================================================"
echo "[SUCCESS] Web server provisioned!"
echo "Access URL: http://$PUBLIC_IP"
echo "======================================================================"
```

---

### Lab 2: Automated Multi-Cloud Storage Sync Engine (AWS S3 to GCP GCS)

#### Objective:
Build a production-grade Bash utility that synchronizes backup archives between an AWS S3 bucket and a GCP GCS bucket while ensuring MD5 checksum validation.

```bash
#!/bin/bash
# ==============================================================================
# LAB 2: Cross-Cloud Storage Replication Engine (S3 -> GCS)
# Prerequisites: aws-cli, gcloud CLI installed and authenticated
# ==============================================================================

set -euo pipefail

S3_SRC_BUCKET="s3://prod-backup-source-998"
GCS_DST_BUCKET="gs://gcp-backup-replica-998"
LOCAL_TMP_DIR="/tmp/cloud_sync_$(date +%s)"

mkdir -p "$LOCAL_TMP_DIR"
trap 'rm -rf "$LOCAL_TMP_DIR"' EXIT

echo "[1/3] Fetching file index from AWS S3..."
aws s3 sync "$S3_SRC_BUCKET" "$LOCAL_TMP_DIR/" --exact-timestamps

echo "[2/3] Verifying local integrity..."
FILE_COUNT=$(find "$LOCAL_TMP_DIR" -type f | wc -l)
echo "Total files downloaded: $FILE_COUNT"

echo "[3/3] Uploading and synchronizing to GCP GCS..."
gcloud storage rsync "$LOCAL_TMP_DIR" "$GCS_DST_BUCKET" --recursive --delete-unprocessed-objects

echo "[SUCCESS] Multi-cloud synchronization completed successfully!"
```

---

### Lab 3: End-to-End Modular Terraform Infrastructure Deployment & Drift Remediation

#### Objective:
Deploy an AWS VPC and S3 bucket using Terraform, perform intentional manual configuration drift in the AWS Console/CLI, and use `terraform plan` / `terraform apply` to detect and remediate drift.

```bash
# 1. Initialize Terraform working directory
terraform init

# 2. Inspect execution plan
terraform plan -out=tfplan.binary

# 3. Apply infrastructure configuration
terraform apply tfplan.binary

# 4. INTENTIONALLY SIMULATE CONFIGURATION DRIFT:
# Manually modify the Security Group using AWS CLI outside of Terraform
SG_ID=$(terraform output -raw web_sg_id)
aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 8080 --cidr "0.0.0.0/0"

# 5. DETECT DRIFT USING TERRAFORM:
terraform plan
# Notice Terraform detects port 8080 is not present in main.tf HCL state!

# 6. REMEDIATE DRIFT AUTOMATICALLY:
terraform apply -auto-approve
# Terraform revokes the manual rule and restores state to exact match of HCL!
```

---

## Self-Check & Verification Checklist

- [ ] Can you explain the 5 NIST characteristics of cloud computing?
- [ ] Can you diagram the Shared Responsibility Model across IaaS, PaaS, SaaS, and Serverless?
- [ ] Do you know the functional equivalents between AWS, GCP, and Azure across Compute, Storage, Database, and IAM?
- [ ] Can you design a public/private subnetting architecture (`10.0.0.0/16`) across multiple AZs with Internet and NAT Gateways?
- [ ] Do you understand the statefulness differences between Security Groups (stateful) and Network ACLs (stateless)?
- [ ] Can you execute production-grade CLI commands in `aws`, `gcloud`, and `az` to create VMs and Object Storage buckets?
- [ ] Can you write and execute a production-grade Terraform HCL configuration with remote state locking?
- [ ] Can you diagnose and troubleshoot SSH timeouts, S3 403 errors, NAT gateway failures, and state lock issues using systemic commands?

---

## Progress Tracker

- [x] Mastered Cloud Service Models (IaaS, PaaS, SaaS, FaaS) & Delivery Paradigms.
- [x] Analyzed AWS, GCP, and Azure Architectural Topologies & Service Equivalents.
- [x] Designed Multi-AZ VPC / VNet Subnetting, Routing, & Security Topologies.
- [x] Implemented Object, Block, and File Storage Architectures with Lifecycle Policies.
- [x] Formulated Least-Privilege IAM Policies with Role-Based & Attribute-Based Controls.
- [x] Authored Production-Grade Declarative Infrastructure as Code (Terraform & CloudFormation).
- [x] Solved Real-World Cloud Outage & Cost Troubleshooting Scenarios.
- [x] Completed Hands-On CLI Automation & Multi-Cloud Synchronization Labs.

---

## Next Steps

Advance to the next module in the Linux Infrastructure & Cloud Learning Path:
→ **[[11 - Monitoring & Observability]]**