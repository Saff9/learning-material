# 23 - Cloud Deployment

> Comprehensive strategies for deploying PostgreSQL in the cloud: AWS RDS, GCP Cloud SQL, Supabase, Serverless, Kubernetes, and IaC (Terraform).

Choosing the right cloud deployment model dictates your maintenance overhead, scaling capabilities, and pricing.

---

## 1. Managed Databases (PaaS)

Platform-as-a-Service models remove the burden of OS patching, backups, and physical replication.

### Amazon Web Services (AWS RDS for PostgreSQL)

AWS RDS is the industry standard for enterprise PostgreSQL deployments.

**Key Features:**
- **Multi-AZ:** Synchronous standby replica in a different Availability Zone. Automatic failover (DNS flip) in ~60 seconds.
- **Read Replicas:** Up to 15 asynchronous read replicas for read-scaling.
- **Automated Backups:** Automated daily snapshots and WAL archiving for Point-In-Time-Recovery (PITR) up to 35 days.
- **RDS Proxy:** Fully managed, highly available PgBouncer alternative for connection pooling.
- **Aurora PostgreSQL:** AWS's custom storage engine compatible with Postgres. Decouples compute from storage. Massively faster replication, auto-scaling storage up to 128TB.

**CLI Deployment Example:**
```bash
aws rds create-db-instance \
  --db-instance-identifier prod-postgres \
  --db-instance-class db.t4g.large \
  --engine postgres \
  --engine-version 16.3 \
  --allocated-storage 100 \
  --storage-type gp3 \
  --master-username rootadmin \
  --master-user-password SecurePass123! \
  --backup-retention-period 7 \
  --multi-az \
  --enable-performance-insights
```

### Google Cloud (GCP Cloud SQL)

Cloud SQL provides highly integrated PostgreSQL deployments on Google Cloud.

**Key Features:**
- Seamless integration with BigQuery (federated queries) and IAM authentication.
- Custom machine types (tune vCPU/RAM ratios exactly to your workload).
- Regional High Availability via synchronous replication.

**CLI Deployment Example:**
```bash
gcloud sql instances create prod-pg \
  --database-version=POSTGRES_16 \
  --cpu=4 --memory=16GB \
  --region=us-central1 \
  --availability-type=REGIONAL \
  --storage-type=SSD --storage-size=100GB \
  --enable-point-in-time-recovery
```

---

## 2. Serverless and Edge PostgreSQL

Serverless PostgreSQL separates compute and storage, allowing databases to auto-scale instantly, branch like code, and scale to zero to save costs.

### Supabase
Supabase is an open-source Firebase alternative built natively on PostgreSQL. It exposes Postgres directly to the frontend safely.

**Key Features:**
- **Row Level Security (RLS):** Supabase relies heavily on native Postgres RLS to ensure users only query data they own directly from client apps.
- **PostgREST:** Instantly turns your database schema into a RESTful API.
- **Realtime:** Subscribes to database changes via Postgres logical replication and broadcasts over WebSockets.
- **Built-in Pooling:** Supabase provisions a PgBouncer (and newer Supavisor) connection pooler on port 6543.

**Connecting:**
```bash
# Direct Connection (Port 5432 - use for migrations/admin)
postgres://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres

# Pooled Connection (Port 6543 - use for serverless functions/app queries)
postgres://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### Neon (Serverless Postgres)
Neon revolutionized Postgres storage by writing a custom storage engine built on Rust that writes to S3.

**Key Features:**
- **Scale to Zero:** Compute instances shut down automatically when idle, reducing costs.
- **Branching:** Instantly clone a multi-TB database in seconds (uses Copy-on-Write) for CI/CD, testing, or isolated development.
- **Bottomless Storage:** Offloads older data directly to cloud object storage.

---

## 3. Kubernetes (CloudNativePG)

For self-managed cloud-agnostic deployments, running stateful workloads on Kubernetes is now mature, primarily via Operators. **CloudNativePG** (created by EnterpriseDB) is the standard.

It provides automated failover, declarative configuration, and continuous backup to S3/GCS.

```yaml
# cluster.yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: prod-cluster
spec:
  instances: 3 # 1 Primary, 2 Replicas
  imageName: ghcr.io/cloudnative-pg/postgresql:16
  postgresql:
    parameters:
      shared_buffers: "1GB"
      max_connections: "500"
  storage:
    size: 50Gi
  backup:
    barmanObjectStore:
      destinationPath: s3://my-bucket/pg-backups/
      s3Credentials:
        accessKeyId:
          name: aws-creds
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: aws-creds
          key: SECRET_ACCESS_KEY
```

---

## 4. Infrastructure as Code (Terraform)

Databases should be provisioned via Infrastructure as Code (IaC) to ensure reproducibility and track infrastructure changes in Git.

**Terraform AWS RDS Example:**
```hcl
resource "aws_db_instance" "production_db" {
  identifier              = "prod-postgres"
  engine                  = "postgres"
  engine_version          = "16.3"
  instance_class          = "db.t4g.medium"
  allocated_storage       = 100
  max_allocated_storage   = 1000 # Enables storage auto-scaling
  
  db_name                 = "myapp_db"
  username                = "dbadmin"
  password                = var.db_password
  
  multi_az                = true
  publicly_accessible     = false
  vpc_security_group_ids  = [aws_security_group.db_sg.id]
  
  backup_retention_period = 7
  copy_tags_to_snapshot   = true
  storage_encrypted       = true
  
  performance_insights_enabled = true
  
  # Prevent accidental deletion
  deletion_protection = true 
}
```

---
*Previous: 22 - AI/Vector | Next: 24 - Internals & Storage*
