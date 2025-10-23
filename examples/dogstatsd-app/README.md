# DogStatsD Sample Application

A sample application that generates various types of DogStatsD metrics.

## Overview

This application generates realistic metrics simulating a web application, including:

- **HTTP Request Metrics**: Request counts, response times, status codes

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DOGSTATSD_HOST` | Hostname/IP of DogStatsD receiver | `localhost` |
| `DOGSTATSD_PORT` | Port of DogStatsD receiver | `8125` |
| `OTLP_ENDPOINT` | OTLP HTTP endpoint (backup) | `http://localhost:4318/v1/metrics` |
| `APP_NAME` | Application name for metrics namespace | `dogstatsd-sample-app` |
| `METRIC_INTERVAL` | Interval between metric batches (seconds) | `10` |
| `NAMESPACE` | Kubernetes namespace (auto-populated) | `default` |
| `POD_NAME` | Pod name (auto-populated) | `unknown-pod` |
| `NODE_NAME` | Node name (auto-populated) | `unknown-node` |

