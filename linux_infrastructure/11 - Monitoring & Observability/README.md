# 11 - Monitoring & Observability

> **Phase:** 2 (Core Infrastructure) · **Time:** ~3 weeks · **Difficulty:** ⭐⭐⭐⭐

## What it is
**Monitoring and observability** are the practices of collecting, analyzing, and acting on data about system health, performance, and user behavior. Observability goes a step further: you should be able to answer *three key questions* from any signal, regardless of how complex the system is:

1. **Where am I?** – Where in the system is an issue occurring?
2. **What is broken?** – What symptoms indicate a problem?
3. **How can I fix it?** – What actions can be taken to resolve or mitigate?

Modern cloud‑native applications generate massive amounts of telemetry data, logs, metrics, and traces. Effective monitoring helps teams maintain reliability, security, and performance, while also enabling capacity planning and cost optimization.

## Why it matters
- **Reliability:** Detect outages before users notice.
- **Performance:** Identify bottlenecks and optimize resource usage.
- **Security:** Spot anomalies, intrusions, and data exfiltration.
- **Cost control:** Monitor usage and identify over‑provisioning.
- **Developer productivity:** Reduce time spent debugging.
- **Business continuity:** Ensure compliance with SLAs and regulatory requirements.

## Core concepts — detailed

### 1. Signal types
| Signal type | Description | Typical tools | Use case |
|---|---|---|---|
| **Metrics** | Quantitative measurements (e.g., CPU usage, request latency, error rate). | Prometheus, Datadog, CloudWatch Metrics, Grafana, Azure Monitor. | Real‑time dashboards, alerting, capacity planning. |
| **Logs** | Unstructured text events (system messages, application logs). | ELK Stack (Elasticsearch, Logstash, Kibana), Splunk, CloudWatch Logs, Azure Monitor Logs. | Troubleshooting, audit trails, anomaly detection. |
| **Traces** | End‑to‑end request flows across distributed services. | Jaeger, Zipkin, OpenTelemetry, AWS X‑Ray, Google Cloud Trace. | Understanding request latency, service dependencies. |

### 2. Metrics collection & storage
- **Push vs. pull:** Prometheus pushes metrics to exporters; some exporters pull data.
- **Scraping:** Prometheus scrapes metrics from exposed `/metrics` endpoints.
- **Retention:** Choose storage duration (hours–days) based on analysis needs.
- **Aggregation:** Rate, sum, histogram for time series.

**Example Prometheus query:** `rate(http_requests_total{method="GET"}[5m])`

### 3. Log collection & analysis
- **Centralized logging:** Forward logs to a centralized system (e.g., ELK, Splunk) via file tailing or HTTP.
- **Log format:** JSON, structured, plain text.
- **Filter/annotation:** Add fields (`level`, `service`, `trace_id`) for easier querying.

**Example: Fluentd pipeline:**
```ruby
<source>
  @type tail
  path /var/log/nginx/access.log
  pos_file /var/log/nginx.pos
  format apache2
  time_format %d/%b/%Y:%H:%M:%S %z
</source>

<match **> **production</strong>**>
  @type elasticsearch
  host elasticsearch.default.svc.cluster.local
  port 9200
</match>
```

### 4. Distributed tracing
- **Instrumentation:** Add tracing headers to requests (W3C Trace Context).
- **Sampling:** Decide on percentage/delayed sampling for cost control.
- **Propagation:** Trace context propagates across services (AWS X‑Ray, OpenTelemetry).
- **Visualization:** Jaeger UI shows service maps, latency distributions.

### 5. Alerting
- **Threshold‑based:** Alert when metric exceeds value (e.g., error rate > 5%).
- **Anomaly detection:** Machine learning (e.g., Azure Monitor, Datadog Anomaly Detection).
- **Correlation:** Combine multiple signals (high error + latency) to reduce false positives.
- **Channels:** Slack, email, PagerDuty, Microsoft Teams, SMS.

**Example Prometheus AlertRule:**
```yaml
title: High Error Rate
expression: rate(http_requests_total{status_code="500"}[5m]) > 0.05
for: 2m
labels:
  severity: critical
actions:
  - "pagerduty"
```

### 6. Dashboarding & visualization
- **Grafana** (open‑source) connects to Prometheus, InfluxDB, Loki, InfluxDB.
- **Cloud provider consoles:** AWS CloudWatch dashboards, GCP Monitoring Insights, Azure Monitor.
- **Business metrics:** Revenue, user sign‑ups, feature adoption.

### 7. Security monitoring
- **Threat detection:** Anomaly detection, intrusion detection systems (Snort, Suricata).
- **Compliance logging:** Record access to sensitive data (PII, financial records).
- **Vulnerability scanning:** Qualys, Nessus, OpenVAS.

### 8. Best practices
- **Instrument early:** Add metrics/logs to code from day one.
- **Avoid log anti‑patterns:** Do not log secrets, PII without masking.
- **Use structured logging:** JSON key/value pairs for easier querying.
- **Sampling wisely:** Reduce load on collection systems.
- **Set up alerts responsibly:** Avoid alert fatigue.

## Free resources — curated for self‑learners

1. **Prometheus Docs:** https://prometheus.io/docs/intro/overview/\n2. **Grafana Docs:** https://grafana.com/docs/\n3. **ELK Stack Setup:** https://www.elastic.co/guide/en/elastic-stack/current/index.html\n4. **AWS CloudWatch Tutorials:** https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring\/\n5. **Google Cloud Monitoring:** https://cloud.google.com/monitoring\/\n6. **Azure Monitor:** https://learn.microsoft.com/en-us/azure/azure-monitor/\n7. **OpenTelemetry:** https://opentelemetry.io/docs/\n8. **Distributed Tracing with Jaeger:** https://www.jaegertracing.io/docs/latest/\n9. **Datadog Learning Center:** https://www.datadoghq.com/learning\n10. **Sentry Docs:** https://docs.sentry.io/ (error tracking)\n
## Practice labs (use free tiers, sandbox environments)

### Lab 1: Setup Prometheus + Node Exporter (Linux server)
```bash
# Install Prometheus
sudo apt update && sudo apt install prometheus
\n# Install node exporter (exporter for system metrics)
sudo apt install prometheus-node-exporter\n\n# Edit prometheus.yml (sample config)
# Add target: localhost:9100\n\n# Start Prometheus\nsudo systemctl start prometheus\nsudo systemctl enable prometheus\n\n# Access dashboard: http://<server-ip>:9090\n```

### Lab 2: Grafana dashboard with Prometheus (google compute)
```bash\n# Install Grafana\nsudo apt install grafana\n\n# Start Grafana\nsudo systemctl start grafana-server\nsudo systemctl enable grafana-server\n\n# Open browser: http://<server-ip>:3000\n# Add Prometheus as data source\n# Import sample dashboard (e.g., \"Node Exporter Full\" from Grafana.com)\n```\n
### Lab 3: ELK Stack (Ubuntu)
```bash\n# Install Elasticsearch, Logstash, Kibana (docker-compose)\ndocker-compose -f /path/to/elk-compose.yml up -d\n\n# Sample docker-compose.yml\nde\nversion: '3.8'\nservices:\n  elasticsearch:\n    image: elasticsearch:8\n    container_name: elasticsearch\n    environment:\n      - \"discovery.type=single-node\"\n      - \"xpack.security.enabled=true\"\n    ports:\n      - \"9200:9200\"\n    volumes:\n      - esdata:/usr/share/elasticsearch/data\n\n  logstash:\n    image: logstash:8\n    container_name: logstash\n    ports:\n      - \"5000:5000\"\n\n  kibana:\n    image: kibana:8\n    container_name: kibana\n    ports:\n      - \"5601:5601\"\n\nvolumes:\n  esdata:\n    driver: local\n```\n\n# Verify\n# http://localhost:5601 (Kibana) -> import pre‑built dashboards\n```\n\n### Lab 4: Basic Prometheus alerting (alertmanager)
```bash\n# Install alertmanager\nsudo apt install prometheus-alertmanager\n\n# Create alertmanager.yml\ncat > alertmanager.yml <<EOF\ndispatched_rules_path: /etc/alertmanager/dispatcher/rules\nroute:\n  receiver: \"default\"\n  routes:\n  - match:\n      severity: critical\n    receiver: \"pagerduty\"\nreceivers:\n- name: \"default\"\n- name: \"pagerduty\"\n  webhook_url: \"https://events.pagerduty.com/integrations/xxx\"\nEOF\n\n# Update prometheus.yml to include alertmanager\n# alert kyt path\n# systemctl restart prometheus\n```\n\n### Lab 10: Google Cloud Monitoring setup\n```bash\n# Enable Monitoring API\ngcloud services enable monitoring.googleapis.com\n\n# Create a custom metric (instance_cpu_utilization)\ngcloud monitoring policies create \
  --policy-from-file=./policy.yaml\n\n# View metric in GCP Console: Monitoring -> Metrics Explorer\n```\n\n## Self‑check (can you…)\n- [ ] Explain differences between metrics, logs, traces.\n- [ ] Install and configure Prometheus + Node Exporter.\n- [ ] Create a basic Grafana dashboard with Prometheus data.\n- [ ] Setup a simple ELK stack for logs.\n- [ ] Configure Prometheus Alertmanager for critical alerts.\n- [ ] Compare cloud provider monitoring services (AWS CloudWatch, GCP Monitoring, Azure Monitor).\n\n## Progress\n- [ ] Installed Prometheus + Node Exporter and scraped metrics.\n- [ ] Set up Grafana dashboard and imported sample panels.\n- [ ] Installed ELK stack and indexed sample logs.\n- [ [ ] Configured Alertmanager rules and tested alerts.\n- [ ] Explored cloud provider monitoring dashboards.\n\n## Next\n→ [[12 - Projects & DevOps Integration]]\n