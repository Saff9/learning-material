# 10 - Cloud Foundations

> **Phase:** 1 (Core Infrastructure) · **Time:** ~3 weeks · **Difficulty:** ⭐⭐⭐⭐

## What it is
**Cloud computing** abstracts computing resources (servers, storage, databases, networking) as on-demand services accessible over the internet. It enables rapid provisioning, elastic scaling, and pay‑as‑you‑go pricing, eliminating the need for physical hardware management.

**Cloud foundations** cover the core concepts, terminology, and service models that form the basis for modern software engineering and DevOps workflows. Understanding cloud platforms is essential for building, deploying, and operating applications at scale.

## Why it matters
- **Scalability:** Automatically adjust resources to match demand.
- **Cost efficiency:** Pay only for what you use, no upfront capital.
- **Global reach:** Deploy applications closer to end users.
- **Reliability & redundancy:** Built‑in failover and disaster recovery.
- **Developer productivity:** Managed services reduce operational overhead.
- **Future‑proof:** Cloud is the dominant paradigm in enterprise IT.

## Core concepts — detailed

### 1. Cloud service models
| Model | Description | Example |
|---|---|---|
| **IaaS** (Infrastructure as a Service) | Provides virtual servers, storage, networking. You manage OS, runtime, apps. | AWS EC2, Google Compute Engine, Azure Virtual Machines |
| **PaaS** (Platform as a Service) | Offers runtime, middleware, development tools. No OS/server management. | AWS Elastic Beanstalk, Google App Engine, Azure App Service |
| **SaaS** (Software as a Service) | Full applications delivered over the internet. No infrastructure or platform management. | Google Workspace, Microsoft 365, Salesforce |

> Most dev‑ops learning focuses on IaaS + PaaS.

### 2. Deployment models
| Model | Description | Typical Use Case |
|---|---|---|
| **Public cloud** | Services offered over the internet, shared infrastructure. | Most startups, web apps. |
| **Private cloud** | Dedicated infrastructure for a single organization (on‑prem or hosted). | Large enterprises, compliance‑heavy sectors. |
| **Hybrid cloud** | Combination of public and private, with orchestration between them. | Businesses needing both control and scalability. |

### 3. Major cloud providers

#### Amazon Web Services (AWS)
- **Core compute:** EC2 (VM), ECS (container), Lambda (serverless).\n- **Storage:** S3 (object), EBS (block), Glacier (archive).\n- **Networking:** VPC (virtual network), Route 53 (DNS), CloudFront (CDN).\n- **Databases:** RDS (relational), DynamoDB (NoSQL), Aurora (MySQL/PostgreSQL compatible).\n- **Management tools:** CloudWatch (monitoring), CloudFormation (IaC), EKS (Kubernetes).

#### Google Cloud Platform (GCP)
- **Compute:** Compute Engine (VM), GKE (managed Kubernetes), Cloud Functions (serverless).\n- **Storage:** Cloud Storage (object), Filestore (NFS), Spanner (global database).\n- **Networking:** VPC, Cloud DNS, Cloud Load Balancing.\n- **Data & AI:** BigQuery (warehouse), Vertex AI (ML), Pub/Sub (messaging).\n- **Managed services:** Cloud SQL, Memorystore (Redis).

#### Microsoft Azure
- **Compute:** Virtual Machines, App Service (web), Azure Functions (serverless), AKS (Kubernetes).\n- **Storage:** Blob Storage (object), Disk Storage (block), Archive Storage.\n- **Networking:** Virtual Network, Azure DNS, Application Gateway.\n- **Databases:** Azure SQL Database, Cosmos DB (NoSQL), Azure Database for MySQL/PostgreSQL.\n- **Management:** Azure Monitor, Resource Manager (IaC via ARM templates).

### 4. Infrastructure as Code (IaC)
IaC lets you define and provision cloud resources declaratively.

#### Terraform (cross‑cloud)
```hcl
provider \"aws\" {
  region = \"us-east-1\"
}

resource \"aws_instance\" \"example\" {
  ami           = \"ami-0c55b159cbfafe1f0\"\n  instance_type = \"t2.micro\"\n  \n  tags = {\n    Name = \"example-instance\"\n  }\n}
```

#### AWS CloudFormation (AWS native)
```yaml\nAWSTemplateFormatVersion: '2010-09-09'\nDescription: \"Hello World CloudFormation example\"\n\nResources:\n  MyEC2Instance:\n    Type: AWS::EC2::Instance\n    Properties:\n      ImageId: ami-0c55b159cbfafe1f0\n      InstanceType: t2.micro\n      Tags:\n      - Key: Name\n        Value: HelloWorld\n```

#### Azure ARM template (JSON)
```json{
  \"\$schema\": \"https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#\",
  \"contentVersion\": \"1.0.0.0\",
  \"parameters\": {},
  \"resources\": [
    {
      \"type\": \"Microsoft.Compute/virtualMachines\",
      \"apiVersion\": \"2021-03-01\",
      \"name\": \"myVM\",
      \"location\": \"eastus\",
      \"properties\": {
        \"hardwareProfile\": { \"vmSize\": \"Standard_B2s\" },
        \"storageProfile\": { \"imageReference\": { \"publisher\": \"Canonical\", \"offer\": \"ubuntu-server-20.04\" } },
        \"osProfile\": { \"adminUsername\": \"azureuser\", \"computerName\": \"myvm\", \"linuxConfiguration\": { \"ssh\": { \"publicKeys\": [ { \"keyData\": \"xxx==\", \"path\": \"/home/azureuser/.ssh/authorized_keys\" } ] } } }
      }
    }
  ]
}
```

### 5. Networking in the cloud
- **Virtual networks:** VPC (AWS), VNet (Azure), VPC (GCP).
- **Subnets:** CIDR blocks for isolation (public vs private).
- **Load balancers:** Application Load Balancer (ALB), Network Load Balancer (NLB) – AWS; Azure Application Gateway, GCP HTTP(S) Load Balancer.
- **DNS:** Route 53, Cloud DNS, Azure DNS.
- **Peering:** Connect VPCs or VNets across accounts/regions.

### 6. Storage services
- **Object storage:** S3 (AWS), Cloud Storage (GCP), Blob Storage (Azure) – scalable, REST API, version control.
- **Block storage:** EBS (AWS), Disk Storage (Azure), Persistent Disk (GCP) – low‑latency, attached to VMs.
- **File storage:** EFS (AWS), Filestore (GCP), Azure Files – shared NFS‑style.

### 7. Security and identity
- **IAM:** AWS IAM policies, GCP IAM roles, Azure RBAC.\n- **Service principals / identities:** Managed identities (AWS, Azure), Service Accounts (GCP).\n- **SSL/TLS:** ACM (AWS), Cloud SSL (GCP), Azure App Registration.\n
### 8. Monitoring and observability
- **Logging:** CloudWatch Logs (AWS), Stackdriver (GCP), Azure Monitor.\n- **Metrics:** CloudWatch Metrics, GCP Monitoring, Azure Metrics.\n- **Tracing:** AWS X‑Ray, GCP Trace, Azure Monitor Application Insights.\n
## Free resources — curated for self‑learners

1. **AWS Training & Certification:** https://aws.amazon.com/training/ (free labs, whitepapers)\n2. **Google Cloud Training:** https://cloud.google.com/training (free codelabs, videos)\n3. **Microsoft Learn:** https://learn.microsoft.com/ (free modules, hands‑on labs)\n4. **Terraform Official Docs:** https://developer.hashicorp.com/terraform/docs\n5. **DevOps Essentials (Coursera):** Cloud computing, IaC, CI/CD - free audit.\n6. **The Cloud Native Computing Foundation (CNCF) Learning Path:** https://www.cncf.io/learning/ (Kubernetes, Helm, etc.)\n7. **AWS Well‑Architected Framework:** https://aws.amazon.com/well-architected/ (free best practices)\n
## Practice labs (use free tier accounts for hands‑on experience)\n
### Lab 1: AWS EC2 and S3\n1. Create an EC2 t2.micro instance with Linux (Amazon Linux 2).\n2. Connect via SSH and install a package (`yum install -y tree`).\n3. Create an S3 bucket using the AWS CLI (`aws s3 mb s3://my-test-bucket-123`).\n4. Upload a file (`echo \"Hello from AWS\" > file.txt` && `aws s3 cp file.txt s3://my-test-bucket-123/`).\n
### Lab 2: GCP Compute Engine and Cloud Storage\n1. Create a Compute Engine VM (`gcloud compute instances create my-instance --zone=us-central1-a --machine-type=e2-micro`).\n2. Install a package (`sudo apt-get update && sudo apt-get install -y curl`).\n3. Create a Cloud Storage bucket (`gsutil mb gs://my-test-bucket-123`).\n4. Upload a file (`echo \"Hello from GCP\" > file.txt && gsutil cp file.txt gs://my-test-bucket-123/`).\n
### Lab 3: Azure VM and Storage\n1. Create a Windows VM using Azure CLI (`az vm create --resource-group myResourceGroup --name myVM --image WindowsServer2019-datacenter --admin-username azureuser --generate-ssh-key`).\n2. Connect via RDP (or SSH) and install a package (`choco install git -y`).\n3. Create a Storage Account (`az storage account create --resource-group myResourceGroup --name mystorageaccount --sku Standard_LRS`).\n4. Upload a blob (`az storage blob upload --container-name mycontainer --name file.txt --file file.txt --account-name mystorageaccount`).\n
### Lab 4: Terraform provisioning (multi‑cloud example)\n```hcl\nprovider \"aws\" {\n  region = \"us-east-1\"\n}\n\nprovider \"google\" {\n  project = \"your-project-id\"\n  region  = \"us-central1\"\n}\n\n# AWS EC2 example\nresource \"aws_instance\" \"aws-ec2\" {\n  ami           = \"ami-0c55b159cbfafe1f0\"\n  instance_type = \"t2.micro\"\n}\n\n# GCP Compute Engine example\nresource \"google_compute_instance\" \"gcp-vm\" {\n  name         = \"gcp-vm\"\n  machine_type = \"e2-micro\"\n  zone         = \"us-central1-a\"\n\n  boot_disk {\n    initialize_params {\n      image = \"debian-11\"\n    }\n  }\n\n  network_interface {\n    network = \"default\"\n  }\n}\n```\n
### Lab eliminites
- Verify Terraform plan and apply (`terraform init`, `terraform plan`, `terraform apply`).

## Self‑check (can you…)\n- [ ] Explain differences between IaaS, PaaS, SaaS.\n- [ ] Compare key services and pricing models of AWS, GCP, Azure.\n- [ ] Create and configure a virtual machine in each major cloud.\n- [ ] Store and retrieve objects in object storage.\n- [ ] Write basic Terraform configuration to provision resources.\n- [ ] Connect to cloud resources via SSH/ RDP.\n\n## Progress\n- [ ] Created VM instances in AWS, GCP, Azure.\n- [ ] Explored object storage and created buckets.\n- [ ] Wrote and applied Terraform configurations.\n- [ ] Managed cloud networking basics.\n- [ ] Compared provider offerings and best‑use cases.\n\n## Next\n→ [[11 - Monitoring & Observability]]\n