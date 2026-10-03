# 11 - Monitoring & Observability: Enterprise Telemetry, Metrics, Logging, Tracing & Infrastructure Alerting

> **Phase:** 2 (Core Infrastructure) · **Time:** ~3 weeks · **Difficulty:** ⭐⭐⭐⭐  
> **Core Focus:** Prometheus TSDB Engine, PromQL Data Analysis, Grafana Visualization, Enterprise ELK/EFK Stack, Grafana Loki, Promtail, OpenTelemetry, Jaeger Tracing, Alertmanager Escalation, System Health Telemetry (eBPF, Node Exporter, Journald), and Production Infrastructure Troubleshooting.

---

## 1. Executive Overview & Architectural Foundations

### What is Monitoring vs. Observability?
In modern cloud-native and enterprise Linux environments, maintaining system uptime and operational performance requires two complementary paradigms:

* **Monitoring (Black-Box / State Inspection):** Tracks the external symptoms of a system. It answers *whether* a system is working by measuring aggregated metrics against predetermined static thresholds (e.g., "Is port 80 open?", "Is CPU utilization above 85%?"). Monitoring tells you when a system is failing.
* **Observability (White-Box / Internal State Inferencing):** Measures the internal state of a system based on the external telemetry outputs it emits (metrics, logs, traces, profiles). Observability allows engineers to answer *why* a system is failing—including novel, unexpected failure modes in complex, distributed microservices—without deploying new code.

```
+-----------------------------------------------------------------------------------+
|                               OBSERVABILITY ECOSYSTEM                             |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                           TELEMETRY GENERATION                              |  |
|  |  +------------------+  +-------------------+  +--------------------------+  |  |
|  |  | Node Exporter    |  | Application Code  |  | eBPF Kernel Probes       |  |  |
|  |  | (OS / HW Metrics)|  | (OTel SDK Traces) |  | (BCC / Cilium / Parca)   |  |  |
|  |  +--------+---------+  +---------+---------+  +------------+-------------+  |  |
|  |           |                      |                         |                |  |
|  |           | (Metrics Scrape)     | (OTLP / gRPC)           | (Profiles)     |  |  |
|  +-----------|----------------------|-------------------------|----------------+  |
|              v                      v                         v                   |
|  +-----------------------------------------------------------------------------+  |
|  |                       COLLECTION & AGGREGATION                              |  |
|  |  +------------------+  +-------------------+  +--------------------------+  |  |
|  |  | Prometheus Server|  | Promtail / Vector |  | OpenTelemetry Collector  |  |  |
|  |  | (TSDB Scraper)   |  | (Log Shipper)     |  | (Metrics/Logs/Traces)    |  |  |
|  |  +--------+---------+  +---------+---------+  +------------+-------------+  |  |
|  +-----------|----------------------|-------------------------|----------------+  |
|              v                      v                         v                   |
|  +-----------------------------------------------------------------------------+  |
|  |                       STORAGE & QUERY ENGINES                               |  |
|  |  +------------------+  +-------------------+  +--------------------------+  |  |
|  |  | Prometheus TSDB  |  | Grafana Loki /    |  | Jaeger / Tempo           |  |  |
|  |  | (Time Series)    |  | Elasticsearch     |  | (Distributed Traces)     |  |  |
|  |  +--------+---------+  +---------+---------+  +------------+-------------+  |  |
|  +-----------|----------------------|-------------------------|----------------+  |
|              v                      v                         v                   |
|  +-----------------------------------------------------------------------------+  |
|  |                       VISUALIZATION & ACTION                                |  |
|  |  +----------------------------------+  +---------------------------------+  |  |
|  |  | Grafana Unified Dashboards       |  | Prometheus Alertmanager         |  |  |
|  |  | (Panels, Variables, Alert UI)    |  | (Grouping, Routing, Slack/PD)   |  |  |
|  |  +----------------------------------+  +---------------------------------+  |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### The Three Core Questions
To achieve full system observability, telemetry must empower site reliability engineers (SREs) and sysadmins to answer three fundamental operational questions:
1. **Where am I?** – Pinpoint the exact service, host, container, or kernel subsystem experiencing degradation.
2. **What is broken?** – Identify the precise symptom (e.g., HTTP 504 Gateway Timeout, kernel memory pressure, disk I/O saturation).
3. **How can I fix it?** – Execute targeted remediation (e.g., restart service, expand filesystem, flush connection pool, rollback deployment).

### SRE Observability Frameworks: 4 Golden Signals, USE & RED Methods

| Framework | Primary Target | Key Telemetry Metrics | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **The 4 Golden Signals** (Google SRE) | User-Facing Applications & Microservices | 1. **Latency** (Time to serve request)<br>2. **Traffic** (Demand placed on system)<br>3. **Errors** (Rate of failed requests)<br>4. **Saturation** (Resource capacity utilization) | Core operational status of distributed user-facing web systems. |
| **The USE Method** (Brendan Gregg) | Infrastructure, Hardware & Operating Systems | 1. **Utilization** (Average time resource was busy)<br>2. **Saturation** (Extra work queued waiting for resource)<br>3. **Errors** (Count of resource error events) | Diagnosing physical server, CPU, memory, disk, and network interface bottlenecks. |
| **The RED Method** (Tom Wilkie) | Microservice Request-Response Architectures | 1. **Rate** (Number of requests per second)<br>2. **Errors** (Number of failing requests per second)<br>3. **Duration** (Amount of time requests take) | High-level service performance dashboards and SLO monitoring. |

---

## 2. Telemetry Signals Deep-Dive: Metrics, Logs, Traces & Profiles

Observability relies on four distinct types of operational data (the "MELT+P" telemetry stack).

### Signal Comparison Matrix

| Signal Type | Nature & Format | Structural Characteristics | Primary Tooling | Best Used For |
| :--- | :--- | :--- | :--- | :--- |
| **Metrics** | Numeric time-series values aggregated over time intervals. | Small storage footprint, high performance, fast aggregation, low cost per datapoint. | Prometheus, InfluxDB, VictoriaMetrics, Datadog. | Real-time monitoring, alerting, SLA/SLO tracking, trends. |
| **Logs** | Discrete, timestamped text or JSON event records emitted by apps/kernel. | High detail, contextual richness, large storage footprint, higher ingestion cost. | Grafana Loki, Elasticsearch, Logstash, Fluentbit, Vector. | Root cause post-mortem investigation, auditing, security analysis. |
| **Traces** | Directed acyclic graphs (DAGs) of spans representing end-to-end request journeys. | Context propagation across process boundaries via unique `TraceID` and `SpanID`. | Jaeger, Grafana Tempo, Zipkin, OpenTelemetry. | Microservice dependency mapping, distributed bottleneck isolation. |
| **Profiles** | Call-stack statistical sampling of CPU execution, memory allocations, thread locks. | Deep code-level insights, stack traces mapped to function call rates. | Pyroscope, Parca, ebpf-profiler, Go pprof. | Code performance optimization, locating memory leaks, CPU flamegraphs. |

### The High-Cardinality Trap in Metrics TSDBs
**Cardinality** refers to the total number of unique time series generated by a metric based on its key-value labels.
* **Low-cardinality label:** `environment="production"` (2 values: prod, staging).
* **High-cardinality label (DANGEROUS):** `user_id="109284"`, `client_ip="192.168.1.45"`, `uuid="a3f89b-..."`.

> ⚠️ **CRITICAL WARNING:** Never attach unbounded attributes (such as user IDs, email addresses, order IDs, or IP addresses) as Prometheus metric labels! Doing so creates millions of unique time series, causing Prometheus TSDB RAM usage to explode and inducing Out-Of-Memory (OOM) kernel crashes. Put high-cardinality attributes into **Logs** or **Traces**, NOT metrics!

---

## 3. Metrics Infrastructure — Prometheus TSDB Engine & Exporters

Prometheus is the de facto CNCF standard time-series database (TSDB) for enterprise metrics monitoring.

### Pull vs. Push Architecture
* **Pull Model (Default):** Prometheus actively scrapes HTTP endpoints exposing metrics in OpenMetrics text format (e.g., `http://10.0.0.15:9100/metrics`) at defined intervals.
  * *Advantages:* Centralized control over scrape frequency, automatic failure detection (if target cannot be reached, it is immediately marked `DOWN`), simple target discovery.
* **Push Model (Pushgateway):** Ephemeral batch or cron jobs push metrics to a Pushgateway, which Prometheus scrapes.
  * *Warning:* Pushgateway is an exception handler for short-lived batch jobs, NOT a general-purpose push target for standard services.

### Prometheus Metric Types

| Type | Description | Behavioral Rules | Code / PromQL Example |
| :--- | :--- | :--- | :--- |
| **Counter** | Cumulative metric that only increases or resets to 0 on service restart. | Never use raw Counter values; always wrap with `rate()` or `increase()`. | `node_network_receive_bytes_total` |
| **Gauge** | Value that can arbitrarily go up or down. | Can be queried directly or smoothed with `avg_over_time()`. | `node_memory_MemAvailable_bytes` |
| **Histogram** | Samples observations into configurable cumulative value buckets. | Calculates quantiles server-side using `histogram_quantile()`. | `http_request_duration_seconds_bucket` |
| **Summary** | Calculates configurable quantiles directly on the client side over a sliding window. | Cannot be aggregated across multiple instances or targets! | `rpc_duration_seconds{quantile="0.99"}` |

### Production Prometheus Configuration (`prometheus.yml`)

```yaml
# /etc/prometheus/prometheus.yml
# Production Enterprise Prometheus Configuration

global:
  scrape_interval: 15s     # How frequently targets are scraped
  evaluation_interval: 15s # How frequently alert rules are evaluated
  scrape_timeout: 10s      # Timeout before scrape request is cancelled

  external_labels:
    datacenter: 'us-east-1'
    cluster: 'prod-k8s-01'

# Alertmanager configuration target
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']
      timeout: 5s

# Rule files containing alert definition logic
rule_files:
  - "/etc/prometheus/rules/*.rules.yml"

scrape_configs:
  # Scrape Prometheus itself
  - job_name: 'prometheus'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['localhost:9090']

  # Linux Host Monitoring via Node Exporter
  - job_name: 'node_exporter'
    scrape_interval: 10s
    file_sd_configs:
      - files:
          - '/etc/prometheus/targets/nodes/*.json'
        refresh_interval: 5m
    static_configs:
      - targets: ['localhost:9100', '192.168.1.10:9100', '192.168.1.11:9100']
        labels:
          tier: 'infrastructure'

  # Nginx Web Servers
  - job_name: 'nginx_exporter'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['192.168.1.20:9113']
        labels:
          service: 'frontend-nginx'

  # Docker Container Metrics (cAdvisor)
  - job_name: 'cadvisor'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8080']
```

### PromQL Deep Dive & Production Query Catalog

PromQL (Prometheus Query Language) allows real-time aggregation and filtering of time-series data.

#### Essential PromQL Operators & Functions
* `rate(v[range])`: Calculates per-second average rate of increase of a counter over a time window. Handles resets automatically.
* `irate(v[range])`: Instant per-second rate of increase based on the last two data points. Highly responsive, best for volatile metrics.
* `histogram_quantile(φ, v)`: Calculates the $\phi$-quantile ($0 \le \phi \le 1$, e.g., 0.95 for 95th percentile) from histogram buckets.
* `predict_linear(v[range], t)`: Predicts the value of gauge $t$ seconds into the future using linear regression based on historical range.

#### 10 Production PromQL Queries for Enterprise Sysadmins

```promql
# 1. Host CPU Utilization Percentage (Across all cores)
# Subtracts idle CPU rate from 100%
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 2. Memory Usage Percentage
# Calculates used memory relative to total memory excluding buffers and cached RAM
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# 3. Disk Space Exhaustion Forecast (Predicts if disk fills up in next 4 hours)
# Triggers if predicted free bytes in 4 hours (14400s) is less than 0
predict_linear(node_filesystem_free_bytes{mountpoint="/"}[1h], 14400) < 0

# 4. Storage Disk Utilization Percentage by Mount Point
100 - ((node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"} / node_filesystem_size_bytes{fstype!~"tmpfs|overlay"}) * 100)

# 5. Network Traffic Ingress (Bits per Second)
rate(node_network_receive_bytes_total{device!="lo"}[5m]) * 8

# 6. HTTP Error Rate Percentage (5xx server errors)
(sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100

# 7. 99th Percentile HTTP Request Latency (in Seconds)
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# 8. Unreachable Monitored Target Detection (Up/Down Status)
# Returns 0 if target is offline, 1 if target is responding
up == 0

# 9. System Load Average Ratio relative to CPU Core Count
# Flags if 5-minute load average exceeds available logical CPU cores
node_load5 / count by (instance) (node_cpu_seconds_total{mode="idle"}) > 1.5

# 10. Linux Pending Systemd Services in Failed State
node_systemd_unit_state{state="failed"} > 0
```

### Node Exporter Setup & Tuning

Node Exporter collects hardware and OS metrics exposed by the Linux kernel `/proc` and `/sys` filesystems.

```bash
# 1. Create dedicated system service account
sudo useradd --system --no-create-home --shell /bin/false node_exporter

# 2. Download and extract binary release
VERSION="1.8.1"
wget https://github.com/prometheus/node_exporter/releases/download/v${VERSION}/node_exporter-${VERSION}.linux-amd64.tar.gz
tar -xvf node_exporter-${VERSION}.linux-amd64.tar.gz
sudo cp node_exporter-${VERSION}.linux-amd64/node_exporter /usr/local/bin/
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter

# 3. Create production Systemd Service Unit (/etc/systemd/system/node_exporter.service)
sudo bash -c 'cat <<EOF > /etc/systemd/system/node_exporter.service
[Unit]
Description=Prometheus Node Exporter
Documentation=https://github.com/prometheus/node_exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter \
  --collector.systemd \
  --collector.processes \
  --collector.filesystem.mount-points-exclude="^/(sys|proc|dev|host|etc)($|/)" \
  --web.listen-address=":9100"
Restart=always
RestartSec=5s
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF'

# 4. Enable and start node_exporter
sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter
sudo systemctl status node_exporter

# 5. Verify metrics endpoint output
curl -s http://localhost:9100/metrics | grep node_cpu_seconds_total | head -n 5
```

---

## 4. Enterprise Centralized Logging — ELK/EFK Stack & Grafana Loki

Logging provides granular historical evidence required to diagnose intermittent failures, security breaches, and software exceptions.

### Log Architecture Matrix: ELK vs. Grafana Loki

| Dimension | ELK Stack (Elasticsearch, Logstash, Kibana) | Grafana Loki + Promtail |
| :--- | :--- | :--- |
| **Indexing Model** | Full-text indexing of every log word and field. | Label-only indexing (similar to Prometheus metric labels). |
| **Resource Footprint** | Heavy RAM/CPU requirements (JVM overhead, large index size). | Ultra-lightweight (minimal RAM, store logs in low-cost Object Storage/S3). |
| **Search Capabilities** | Complex full-text search, regex, geo-ip, aggregations. | Filter stream by labels, then regex tail scan (`|~ "error"`). |
| **Integration** | Kibana dashboards, Lucene query syntax. | Native Grafana integration, seamless correlation with Prometheus metrics. |

### Production Logstash Pipeline (`logstash.conf`)

```ruby
# /etc/logstash/conf.d/01-nginx-pipeline.conf
# Logstash Pipeline for Ingesting and Parsing Nginx Access Logs

input {
  beats {
    port => 5044
  }
  file {
    path => "/var/log/nginx/access.log"
    start_position => "beginning"
    sincedb_path => "/var/lib/logstash/sincedb_nginx"
    type => "nginx-access"
  }
}

filter {
  if [type] == "nginx-access" {
    # Parse standard Combined Nginx Log Format
    grok {
      match => { "message" => "%{COMBINEDAPACHELOG}+%{GREEDYDATA:extra_fields}" }
      remove_field => [ "message" ]
    }
    
    # Convert HTTP response code and byte count to numeric types
    mutate {
      convert => {
        "response" => "integer"
        "bytes" => "integer"
      }
    }
    
    # Parse timestamp into standardized ISO8601 date
    date {
      match => [ "timestamp" , "dd/MMM/yyyy:HH:mm:ss Z" ]
      target => "@timestamp"
      remove_field => [ "timestamp" ]
    }

    # Enrich IP addresses with Geographical Location data
    geoip {
      source => "clientip"
      target => "geoip"
    }
  }
}

output {
  elasticsearch {
    hosts => ["http://elasticsearch.internal:9200"]
    index => "logstash-nginx-%{+YYYY.MM.dd}"
    user => "logstash_internal"
    password => "${LOGSTASH_PASSWORD}"
  }
}
```

### Production Promtail Configuration for Grafana Loki (`promtail-config.yaml`)

```yaml
# /etc/promtail/promtail-config.yaml
# Production Promtail Log Collector Config

server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /var/log/promtail/positions.yaml

clients:
  - url: http://loki.internal:3100/loki/api/v1/push

scrape_configs:
  # System Logs Scraping (syslog & auth.log)
  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: varlogs
          host: node-01.prod.internal
          __path__: /var/log/*.log

  # Nginx Web Server Log Scraping with JSON Parser Stage
  - job_name: nginx
    static_configs:
      - targets:
          - localhost
        labels:
          job: nginx
          env: production
          __path__: /var/log/nginx/*access.log

    pipeline_stages:
      # Parse regex for Nginx logs
      - regex:
          expression: '^(?P<remote_addr>[\w\.]+) - (?P<remote_user>[^ ]*) \[(?P<time_local>.*?)\] "(?P<request_method>[A-Z]+) (?P<request_uri>[^ ]*) HTTP/(?P<http_version>[\d\.]+)" (?P<status>\d+) (?P<body_bytes_sent>\d+)'
      # Extract extracted fields into Loki labels
      - labels:
          status:
          request_method:
```

### LogQL Query Language Reference

LogQL is Loki's query language, modeled directly after PromQL.

```logql
# 1. Stream Selector: Filter logs by job and status code
{job="nginx", env="production"} |= "error" != "favicon"

# 2. Regex Match: Locate HTTP 5xx errors or connection timeouts
{job="nginx"} |~ "(5[0-9]{2}|Timeout connecting)"

# 3. Log Line JSON Parser & Label Extraction
{job="app"} | json | status_code >= 500 | line_format "Request to {{.uri}} failed with {{.status_code}}"

# 4. Metric Query: Calculate rate of log lines per second over 5m
rate({job="varlogs"} |= "CRITICAL"[5m])

# 5. Metric Query: Calculate 99th percentile of response time extracted from logs
quantile_over_time(0.99, {job="nginx"} | unwrap response_time [5m]) by (host)
```

---

## 5. Distributed Tracing & APM — OpenTelemetry & Jaeger

As monoliths evolve into microservices, tracing a single user request through dozens of network hops requires distributed context propagation.

### Core Tracing Concepts
* **Trace:** The overall journey of a request across a distributed system, identified by a globally unique 128-bit `TraceID`.
* **Span:** A single named, timed segment of execution work within a trace (e.g., executing a SQL query, calling a REST API). Spans contain start/end timestamps, tags, logs, and a `SpanID` & `ParentSpanID`.
* **Context Propagation:** The mechanism of passing tracing headers (W3C Trace Context standard: `traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`) across HTTP/gRPC transport boundaries.

### Production OpenTelemetry Collector Configuration (`otel-collector-config.yaml`)

```yaml
# /etc/otelcol/config.yaml
# OpenTelemetry Collector Production Pipeline

receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  # Memory Limiter prevents OTel Collector from running out of RAM
  memory_limiter:
    check_interval: 1s
    limit_percentage: 75
    spike_limit_percentage: 20

  # Batch Spans before sending to improve throughput
  batch:
    send_batch_size: 1000
    timeout: 1s
    send_batch_max_size: 1500

exporters:
  # Export traces to Jaeger
  otlp/jaeger:
    endpoint: "jaeger-collector.internal:4317"
    tls:
      insecure: true

  # Export metrics to Prometheus Remote Write
  prometheusremotewrite:
    endpoint: "http://prometheus.internal:9090/api/v1/write"

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp/jaeger]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheusremotewrite]
```

---

## 6. Enterprise Alerting & Incident Escalation — Alertmanager

Alerting must be actionable, symptom-based, and noise-free to prevent operational **alert fatigue**.

### Prometheus Alert Rules Definition (`alerts.rules.yml`)

```yaml
# /etc/prometheus/rules/infrastructure.rules.yml
groups:
  - name: infrastructure_alerts
    rules:
      # Target Down Alert
      - alert: InstanceDown
        expr: up == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Instance {{ $labels.instance }} is offline"
          description: "Prometheus host target {{ $labels.instance }} of job {{ $labels.job }} has been unreachable for more than 2 minutes."

      # Storage Exhaustion Alert
      - alert: HostDiskSpaceFillingFast
        expr: (node_filesystem_free_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10 and predict_linear(node_filesystem_free_bytes{mountpoint="/"}[1h], 14400) < 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Disk space on {{ $labels.instance }} filling rapidly"
          description: "Mountpoint '/' has less than 10% free space remaining and is predicted to run out of disk space within 4 hours."

      # High HTTP 5xx Error Rate Alert
      - alert: HighHTTPErrorRate
        expr: (sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100 > 5
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "High HTTP 5xx Error Rate detected on service {{ $labels.service }}"
          description: "Service {{ $labels.service }} HTTP error rate is currently {{ $value | printf \"%.2f\" }}% over the last 5 minutes."
```

### Production Alertmanager Routing Configuration (`alertmanager.yml`)

```yaml
# /etc/alertmanager/alertmanager.yml
# Production Alertmanager Routing & Receiver Configuration

global:
  resolve_timeout: 5m
  slack_api_url: 'https://example.com/slack-webhook-placeholder'

# Grouping rules prevent alert storms by aggregating similar alerts
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack-default'

  # Nested routing tree for escalation
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      continue: true

    - match:
        severity: warning
      receiver: 'slack-warnings'

# Alert Inhibition Rules (Suppress secondary alerts during root outages)
inhibit_rules:
  - source_match:
      alertname: 'InstanceDown'
    target_match_re:
      alertname: '.*'
    equal: ['instance']

receivers:
  - name: 'slack-default'
    slack_configs:
      - channel: '#ops-monitoring'
        send_resolved: true
        text: "Summary: {{ .CommonAnnotations.summary }}\nDescription: {{ .CommonAnnotations.description }}"

  - name: 'slack-warnings'
    slack_configs:
      - channel: '#ops-warnings'
        send_resolved: true

  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_INTEGRATION_KEY'
        send_resolved: true
```

---

## 7. Visualization & Dashboard Engineering — Grafana Masterclass

Grafana unifies metrics, logs, and traces into centralized, interactive production dashboards.

### Dashboard Architecture Best Practices
1. **Executive / High-Level View:** Top-line SLOs, uptime, overall error rate, global request rate.
2. **Service / Application View:** RED method metrics (Request Rate, Error Percentage, Latency Quantiles), active thread pools.
3. **Infrastructure Node View:** USE method metrics (CPU utilization per core, RAM breakdown, Disk IOPS, Network Interface drops).

### Automated Grafana Datasource Provisioning (`datasources.yaml`)

```yaml
# /etc/grafana/provisioning/datasources/prometheus_loki.yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
    jsonData:
      timeInterval: "15s"
      httpMethod: "POST"

  - name: Loki
    type: loki
    access: proxy
    url: http://localhost:3100
    jsonData:
      maxLines: 1000
      derivedFields:
        - name: "TraceID"
          matcherRegex: "trace_id=(\\w+)"
          url: "http://localhost:16686/trace/$${__value.raw}"
```

---

## 8. Real-World Infrastructure Scenarios & System Administration

### Scenario 1: Debugging a CPU Spiking Linux Server
* **Symptom:** Prometheus triggers `HostHighCPUUtilization` alert on `node-web-03`. Load average spikes to 28.5 on a 8-core host.
* **Diagnosis Workflow:**
  1. Inspect Grafana CPU panel: Determine whether CPU time is spent in `user` space, `system` (kernel) space, or `iowait`.
  2. Execute remote SSH diagnostic:
     ```bash
     # Inspect top CPU consuming processes in real-time
     top -b -n 1 -o %CPU | head -n 15

     # Isolate high kernel sys-calls or context switching
     pidstat -wt 1 5
     ```
  3. If high `iowait`, inspect storage IOPS saturation:
     ```bash
     iostat -xz 1 5
     ```
* **Root Cause:** A misconfigured batch script initiated unthrottled log compaction, saturating CPU `iowait` and locking file descriptors.
* **Remediation:** Kill script PID, apply cgroups v2 resource limit (`CPUQuota=200%`) in the systemd unit file.

### Scenario 2: Investigating a Silent Memory Leak in Web Microservices
* **Symptom:** Node RAM consumption slowly trends upward over 7 days until kernel **OOM-Killer** terminates the service process.
* **Diagnosis Workflow:**
  1. Query Prometheus PromQL memory trend:
     ```promql
     predict_linear(node_memory_MemAvailable_bytes[24h], 86400) < 0
     ```
  2. Verify kernel Out-Of-Memory termination events in system journal:
     ```bash
     sudo journalctl -k -g "Out of memory" --no-pager
     ```
  3. Locate the killed process details:
     ```bash
     dmesg -T | grep -i -C 3 "killed process"
     ```
* **Remediation:** Set strict Cgroups memory limits in service unit (`MemoryMax=4G`, `MemoryHigh=3.5G`) so systemd restarts the service gracefully before kernel host instability occurs.

### Scenario 3: Cascading Microservice Latency Outage via Distributed Tracing
* **Symptom:** E-commerce checkout API latency spikes from 120ms to 8,500ms. Frontend returns HTTP 504.
* **Diagnosis Workflow:**
  1. Open Grafana Latency Heatmap panel and filter by HTTP status 504.
  2. Jump to Jaeger UI using correlated `TraceID` linked in Loki log lines.
  3. Inspect Trace DAG visualization: Identify that `checkout-service` -> `inventory-service` call succeeds in 15ms, but `payment-gateway-proxy` span hangs for 8,000ms waiting on database lock.
* **Root Cause:** Database missing composite index on `transactions` table during payment status validation.
* **Remediation:** Create missing SQL database index; configure aggressive client-side connection timeout (2000ms) with circuit breaker pattern.

---

## 9. Production Troubleshooting Matrix

| Issue Symptom | Probable Root Cause | Verification & Diagnostic Command | Targeted Resolution |
| :--- | :--- | :--- | :--- |
| Prometheus target status shows `DOWN` with `connection refused`. | Exporter daemon is stopped or listening on incorrect network interface. | `ss -tulnp \| grep 9100`<br>`curl -I http://target-ip:9100/metrics` | Start exporter service via systemd; verify firewall port access (`sudo ufw allow 9100/tcp`). |
| Prometheus TSDB crashes with `fatal error: runtime: out of memory`. | High-cardinality label explosion or oversized memory chunk cache. | `promtool check metrics`<br>`journalctl -u prometheus -n 100` | Remove high-cardinality labels (IPs/user IDs); decrease `storage.tsdb.retention.time` or scale host RAM. |
| Logstash pipeline stops ingesting logs (Backpressure). | Elasticsearch cluster status is `RED` or log parsing grok error loop. | `curl -XGET http://localhost:9200/_cluster/health?pretty`<br>`tail -f /var/log/logstash/logstash-plain.log` | Resolve ES disk space watermarks (`cluster.routing.allocation.disk.watermark.HIGH`); fix broken Grok syntax. |
| Promtail fails to push logs to Loki (`400 Bad Request: entry out of order`). | Log timestamps arrive out of chronological order or system clock drift. | `chronyc tracking`<br>`promtail -config.file=/etc/promtail/promtail-config.yaml --dry-run` | Enable NTP time synchronization (`timedatectl set-ntp true`); configure Promtail `drop_timestamp_of_out_of_order_stands: true`. |
| Alertmanager does not deliver Slack/PagerDuty notifications. | Invalid webhook URL, proxy restriction, or matching alert inhibition rule. | `curl -XPOST http://localhost:9093/api/v2/alerts`<br>`journalctl -u alertmanager -n 50` | Verify webhook URL credentials; check `inhibit_rules` in `alertmanager.yml` to confirm alerts aren't silenced. |
| Grafana panel displays `Data source parsing error` or missing series. | PromQL query syntax error or datasource proxy connection timeout. | Check browser DevTools Network tab for HTTP status and response payload on `/api/ds/query`. | Fix PromQL query syntax; verify data source URL configuration inside Grafana Admin settings. |

---

## 10. Hands-On Production Practice Labs

### Lab 1: Deploy Prometheus + Node Exporter + Alertmanager Infrastructure on Systemd

**Objective:** Install, configure, and secure a complete metrics and alerting stack on a local Linux server.

```bash
#!/usr/bin/env bash
# Production Installation Script for Prometheus & Alertmanager

set -euo pipefail

PROM_VERSION="2.52.0"
ALERT_VERSION="0.27.0"

# 1. Create Dedicated Service Accounts
sudo useradd --system --no-create-home --shell /bin/false prometheus || true
sudo useradd --system --no-create-home --shell /bin/false alertmanager || true

# 2. Create Directory Structures
sudo mkdir -p /etc/prometheus /var/lib/prometheus /etc/alertmanager /var/lib/alertmanager

# 3. Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v${PROM_VERSION}/prometheus-${PROM_VERSION}.linux-amd64.tar.gz
tar -xvf prometheus-${PROM_VERSION}.linux-amd64.tar.gz
sudo cp prometheus-${PROM_VERSION}.linux-amd64/prometheus /usr/local/bin/
sudo cp prometheus-${PROM_VERSION}.linux-amd64/promtool /usr/local/bin/
sudo cp -r prometheus-${PROM_VERSION}.linux-amd64/consoles /etc/prometheus/
sudo cp -r prometheus-${PROM_VERSION}.linux-amd64/console_libraries /etc/prometheus/
sudo chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus

# 4. Install Alertmanager
wget https://github.com/prometheus/alertmanager/releases/download/v${ALERT_VERSION}/alertmanager-${ALERT_VERSION}.linux-amd64.tar.gz
tar -xvf alertmanager-${ALERT_VERSION}.linux-amd64.tar.gz
sudo cp alertmanager-${ALERT_VERSION}.linux-amd64/alertmanager /usr/local/bin/
sudo cp alertmanager-${ALERT_VERSION}.linux-amd64/amtool /usr/local/bin/
sudo chown -R alertmanager:alertmanager /etc/alertmanager /var/lib/alertmanager

# 5. Validate Tool Installation
promtool --version
amtool --version
```

---

### Lab 2: Auto-Provision Grafana with Prometheus & Loki Data Sources via Code

**Objective:** Deploy Grafana and configure data sources using declarative infrastructure provisioning files.

```bash
# 1. Add Grafana Repository and Install
sudo apt-get install -y apt-transport-https software-properties-common wget
sudo mkdir -p /etc/apt/keyrings/
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt-get update && sudo apt-get install -y grafana

# 2. Inject Datasource Provisioning Manifest
sudo bash -c 'cat <<EOF > /etc/grafana/provisioning/datasources/default.yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
EOF'

# 3. Start Grafana Service
sudo systemctl daemon-reload
sudo systemctl enable --now grafana-server
sudo systemctl status grafana-server

# Verify web port accessibility
curl -s http://localhost:3000/api/health
```

---

### Lab 3: Build a Production Log Pipeline with Loki & Promtail for Nginx

**Objective:** Deploy Loki and Promtail, tail `/var/log/nginx/access.log`, and stream logs to Loki.

```bash
# 1. Download Loki and Promtail Binaries
LOKI_VER="3.0.0"
wget https://github.com/grafana/loki/releases/download/v${LOKI_VER}/loki-linux-amd64.zip
wget https://github.com/grafana/loki/releases/download/v${LOKI_VER}/promtail-linux-amd64.zip
unzip loki-linux-amd64.zip && sudo mv loki-linux-amd64 /usr/local/bin/loki
unzip promtail-linux-amd64.zip && sudo mv promtail-linux-amd64 /usr/local/bin/promtail

# 2. Write Minimal Production Loki Config
sudo mkdir -p /etc/loki /tmp/loki
sudo bash -c 'cat <<EOF > /etc/loki/loki-config.yaml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /tmp/loki
  storage:
    filesystem:
      chunks_directory: /tmp/loki/chunks
      rules_directory: /tmp/loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h
EOF'

# 3. Test Loki Execution
/usr/local/bin/loki -config.file=/etc/loki/loki-config.yaml &
sleep 3
curl -s http://localhost:3100/ready
```

---

### Lab 4: End-to-End Alert Pipeline & Incident Simulation

**Objective:** Trigger a simulated CPU load spike to verify that Prometheus evaluates alert rules, dispatches to Alertmanager, and generates notifications.

```bash
# 1. Install 'stress' utility to generate CPU load
sudo apt-get install -y stress

# 2. Trigger high CPU load across all available cores for 3 minutes
stress --cpu $(nproc) --timeout 180s

# 3. Query Prometheus to verify rule activation in real-time
curl -s 'http://localhost:9090/api/v1/alerts' | grep -i "HostHighCPUUtilization"
```

---

## 11. Self-Check & Knowledge Verification

Can you confidently execute and explain all of the following core competencies?

- [ ] Explain the fundamental differences between **Metrics**, **Logs**, **Traces**, and **Profiles**.
- [ ] Differentiate between SRE operational frameworks: **4 Golden Signals**, **USE Method**, and **RED Method**.
- [ ] Identify and prevent the **high-cardinality label explosion** trap in Prometheus TSDB.
- [ ] Write and optimize complex **PromQL** queries using `rate()`, `histogram_quantile()`, and `predict_linear()`.
- [ ] Install, configure, and secure `node_exporter` as a systemd background service.
- [ ] Construct production-grade `prometheus.yml` configuration files with dynamic target discovery.
- [ ] Build log ingestion pipelines using **ELK Stack** (`logstash.conf`) and **Grafana Loki** (`promtail-config.yaml`).
- [ ] Query and filter logs using **LogQL** stream selectors, regex parsers, and metric transformations.
- [ ] Configure OpenTelemetry Collector (`otel-collector-config.yaml`) to receive, process, and export distributed traces to Jaeger.
- [ ] Write alert rules (`alerts.rules.yml`) with severity routing, threshold duration (`for:`), and Go templating annotations.
- [ ] Configure **Alertmanager** routing trees, grouping, inhibition rules, and Slack/PagerDuty notification receivers.
- [ ] Provision Grafana data sources and dashboards declaratively via infrastructure-as-code configuration files.
- [ ] Diagnose real-world server outages: CPU saturation, memory leaks (OOM-killer), disk space exhaustion, and network latency bottlenecks.

---

## 12. Next Steps & Related Modules

- **Next Module:** Continue with cloud foundations, CI/CD, and IaC pipelines in the later infrastructure modules.
- **Related Fundamentals:**
  - [04 - System Services](../04%20-%20System%20Services/README.md) — Systemd unit management and `journalctl` logging.
  - [07 - Networking](../07%20-%20Networking/README.md) — Network interface metrics, sockets, and port monitoring.
  - [08 - Containers](../08%20-%20Containers/README.md) — Container resource metrics with cAdvisor and Docker telemetry.