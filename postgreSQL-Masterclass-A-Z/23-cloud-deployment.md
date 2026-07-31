# 23 - Cloud Deployment

> AWS RDS, GCP Cloud SQL, Azure, Neon, Supabase, Kubernetes, and Terraform.

---

## AWS RDS

```bash
aws rds create-db-instance \
  --db-instance-identifier my-postgres \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 18.2 \
  --allocated-storage 20 \
  --master-username admin \
  --master-user-password SecurePass123! \
  --backup-retention-period 7 \
  --enable-performance-insights \
  --multi-az
```

### RDS Features
- Automated backups
- Multi-AZ failover
- Read replicas
- Performance Insights
- Enhanced Monitoring

---

## GCP Cloud SQL

```bash
gcloud sql instances create my-postgres \
  --database-version=POSTGRES_18 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --availability-type=REGIONAL \
  --backup-start-time=03:00 \
  --enable-point-in-time-recovery
```

---

## Neon (Serverless)

```bash
# Connection string
# postgres://user:pass@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require

# Features:
# - Auto-scaling compute to zero
# - Branching (copy DB for dev/test)
# - Time-travel restore
```

---

## Supabase

```bash
# Connection via pooling (PgBouncer):
# postgres://postgres.xxx:[PASS]@aws-0-us-east-1.pooler.supabase.com:6543/postgres

# Features:
# - PostgreSQL + Realtime + Auth + Storage
# - Row Level Security
# - Edge Functions
```

---

## Kubernetes (CloudNativePG)

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: appdb
spec:
  instances: 3
  storage:
    size: 10Gi
  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "256MB"
  resources:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
```

---

## Terraform

```hcl
resource "aws_db_instance" "postgres" {
  identifier           = "my-postgres"
  engine              = "postgres"
  engine_version      = "18.2"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "admin"
  password            = var.db_password
  backup_retention_period = 7
  multi_az            = true
  storage_encrypted   = true
}
```

---
*Previous: 22 - AI/Vector | Next: 24 - Internals & Storage*
