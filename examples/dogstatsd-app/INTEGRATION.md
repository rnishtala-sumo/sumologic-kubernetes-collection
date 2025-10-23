# StatsD Integration with Prometheus Node Exporter

This document explains how the DogStatsD sample application integrates with the Prometheus Node Exporter using a statsd-exporter sidecar.

## Architecture Overview

```
┌─────────────────────┐    UDP:8125     ┌──────────────────────────────────┐
│                     │   (DogStatsD)   │         Node Exporter Pod        │
│  Sample App Pod     ├─────────────────┤                                  │
│                     │                 │  ┌─────────────┐ ┌─────────────┐ │
│ dogstatsd-generator │                 │  │node-exporter│ │statsd-export│ │
└─────────────────────┘                 │  │   :9100     │ │er   :9102   │ │
                                        │  └─────────────┘ └─────────────┘ │
                                        └──────────────────────────────────┘
                                                     │
                                                     │ HTTP:9102
                                                     │ (Prometheus format)
                                                     ▼
                                        ┌──────────────────────────────────┐
                                        │     OpenTelemetry Collector      │
                                        │                                  │
                                        │  ┌─────────────────────────────┐ │
                                        │  │   Prometheus Receiver       │ │
                                        │  │   (scrapes :9102/metrics)   │ │
                                        │  └─────────────────────────────┘ │
                                        └──────────────────────────────────┘
                                                     │
                                                     ▼
                                        ┌──────────────────────────────────┐
                                        │         Sumo Logic               │
                                        └──────────────────────────────────┘
```

## How It Works

1. **DogStatsD Metrics Generation**: The sample application generates various types of metrics (counters, gauges, histograms) and sends them via UDP to port 8125.

2. **StatsD Sidecar Reception**: The `statsd-exporter` sidecar container running alongside the prometheus-node-exporter receives the UDP packets on port 8125.

3. **Metric Conversion**: The statsd-exporter converts DogStatsD protocol metrics into Prometheus format and exposes them on port 9102 at the `/metrics` endpoint.

4. **Prometheus Scraping**: The OpenTelemetry Collector's prometheus receiver scrapes both:
   - Node metrics from node-exporter on port 9100
   - StatsD metrics from statsd-exporter on port 9102

5. **Forwarding to Sumo Logic**: The collector processes and forwards all metrics to Sumo Logic.

## Benefits of This Approach

### 1. **Unified Collection Point**
- All node-level metrics (system + application) collected from a single pod
- Consistent labeling and metadata across metric types

### 2. **Prometheus Integration**
- Native Prometheus format for better compatibility
- Leverages existing Prometheus scraping infrastructure
- Supports all Prometheus metric types and labels

### 4. **Scalability**
- DaemonSet deployment scales with cluster nodes

## Configuration Details

### Node Exporter Sidecar Configuration

The statsd-exporter sidecar is configured with:

```yaml
sidecars:
  - name: statsd-exporter
    image: prom/statsd-exporter:v0.27.1
    ports:
      - name: statsd-udp
        containerPort: 8125
        protocol: UDP
      - name: statsd-metrics
        containerPort: 9102
        protocol: TCP
    args:
      - --statsd.listen-udp=:8125          # Listen for StatsD on UDP 8125
      - --statsd.cache-size=1000           # Cache for metric aggregation
      - --statsd.event-queue-size=10000    # Queue size for incoming events
      - --statsd.event-flush-threshold=1000 # Flush when queue reaches threshold
      - --statsd.event-flush-interval=200ms # Flush interval
      - --web.listen-address=:9102         # Prometheus metrics endpoint
      - --web.telemetry-path=/metrics      # Metrics path
      - --log.level=info                   # Logging level
```

### Service Configuration

```yaml
service:
  ports:
    - name: statsd-udp
      port: 8125
      targetPort: 8125
      protocol: UDP
    - name: statsd-metrics
      port: 9102
      targetPort: 9102
      protocol: TCP
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "9102"
    prometheus.io/path: "/metrics"
```

## Metric Format Conversion

### DogStatsD Input Format
```
# Counter
my_app.http.requests:1|c|#status:200,method:GET

# Gauge  
my_app.memory.usage:512|g|#pod:web-1

# Histogram
my_app.response_time:123.45|h|#endpoint:/api/users
```

### Prometheus Output Format
```
# Counter (becomes Prometheus counter)
my_app_http_requests_total{status="200",method="GET"} 1

# Gauge (becomes Prometheus gauge)
my_app_memory_usage{pod="web-1"} 512

# Histogram (becomes Prometheus histogram with buckets)
my_app_response_time_bucket{endpoint="/api/users",le="0.1"} 0
my_app_response_time_bucket{endpoint="/api/users",le="0.5"} 1
my_app_response_time_sum{endpoint="/api/users"} 123.45
my_app_response_time_count{endpoint="/api/users"} 1
```
