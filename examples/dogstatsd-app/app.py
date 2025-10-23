#!/usr/bin/env python3
"""
DogStatsD Metrics Generator

A sample application that generates various types of DogStatsD metrics.
"""

import os
import time
import random
import logging
import signal
import sys
from threading import Thread, Event
import socket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DogStatsDMetricsGenerator:
    def __init__(self):
        # Configuration from environment variables
        self.dogstatsd_host = os.getenv('DOGSTATSD_HOST', 'localhost')
        self.dogstatsd_port = int(os.getenv('DOGSTATSD_PORT', '8125'))
        self.app_name = os.getenv('APP_NAME', 'dogstatsd-sample-app')
        self.namespace = os.getenv('NAMESPACE', 'default')
        self.pod_name = os.getenv('POD_NAME', 'unknown-pod')
        self.node_name = os.getenv('NODE_NAME', 'unknown-node')
        self.metric_interval = int(os.getenv('METRIC_INTERVAL', '10'))
        
        # Initialize DogStatsD UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.statsd_address = (self.dogstatsd_host, self.dogstatsd_port)
        
        # Common tags
        self.common_tags = [
            f'namespace:{self.namespace}',
            f'pod:{self.pod_name}',
            f'node:{self.node_name}',
            f'app:{self.app_name}',
            'environment:test'
        ]
        
        # Control variables
        self.stop_event = Event()
        self.metrics_thread = None
        
        # Metric state for realistic simulation
        self.request_count = 0
        self.error_count = 0
        self.cpu_usage = 50.0
        self.memory_usage = 512.0
        self.active_connections = 0
        
        logger.info(f"Initialized DogStatsD generator")
        logger.info(f"DogStatsD target: {self.dogstatsd_host}:{self.dogstatsd_port}")
        logger.info(f"Metric interval: {self.metric_interval}s")

    def _send_dogstatsd_metric(self, metric_name, value, metric_type, tags=None):
        """Send a DogStatsD metric via UDP"""
        try:
            all_tags = self.common_tags[:]
            if tags:
                all_tags.extend(tags)
            
            tag_string = ','.join(all_tags) if all_tags else ''
            
            if metric_type == 'c':  # counter
                message = f"{self.app_name}.{metric_name}:{value}|c"
            elif metric_type == 'g':  # gauge
                message = f"{self.app_name}.{metric_name}:{value}|g"
            elif metric_type == 'h':  # histogram
                message = f"{self.app_name}.{metric_name}:{value}|h"
            elif metric_type == 't':  # timer
                message = f"{self.app_name}.{metric_name}:{value}|ms"
            else:
                message = f"{self.app_name}.{metric_name}:{value}|{metric_type}"
            
            if tag_string:
                message += f"|#{tag_string}"
            
            self.socket.sendto(message.encode('utf-8'), self.statsd_address)
            
            # Debug logging every 50th metric to avoid spam
            if random.randint(1, 50) == 1:
                logger.debug(f"Sent DogStatsD metric: {message}")
            
        except Exception as e:
            logger.error(f"Failed to send DogStatsD metric: {e}")

    def increment(self, metric_name, value=1, tags=None):
        """Send a counter metric"""
        self._send_dogstatsd_metric(metric_name, value, 'c', tags)

    def gauge(self, metric_name, value, tags=None):
        """Send a gauge metric"""
        self._send_dogstatsd_metric(metric_name, value, 'g', tags)

    def histogram(self, metric_name, value, tags=None):
        """Send a histogram metric"""
        self._send_dogstatsd_metric(metric_name, value, 'h', tags)

    def timer(self, metric_name, value, tags=None):
        """Send a timer metric"""
        self._send_dogstatsd_metric(metric_name, value, 't', tags)

    def generate_web_metrics(self):
        """Generate realistic web application metrics"""
        # Simulate HTTP requests
        status_codes = ['200', '201', '400', '404', '500']
        methods = ['GET', 'POST', 'PUT', 'DELETE']
        endpoints = ['/api/users', '/api/orders', '/api/products', '/health', '/metrics']
        
        # Generate random request
        status = random.choices(status_codes, weights=[70, 10, 10, 5, 5])[0]
        method = random.choice(methods)
        endpoint = random.choice(endpoints)
        
        # Response time (realistic distribution)
        if status == '500':
            response_time = random.uniform(2.0, 10.0)  # Errors take longer
        elif endpoint == '/health':
            response_time = random.uniform(0.001, 0.01)  # Health checks are fast
        else:
            response_time = random.uniform(0.05, 1.5)  # Normal requests
        
        tags = [f'status_code:{status}', f'method:{method}', f'endpoint:{endpoint}']
        
        # Send DogStatsD metrics
        self.increment('http.requests', 1, tags)
        self.histogram('http.response_time', response_time, tags)
        
        if status.startswith('5') or status.startswith('4'):
            self.increment('http.errors', 1, tags)
            self.error_count += 1
        
        self.request_count += 1

    def generate_system_metrics(self):
        """Generate system-level metrics"""
        # CPU usage (with realistic variation)
        self.cpu_usage += random.uniform(-5, 5)
        self.cpu_usage = max(0, min(100, self.cpu_usage))
        
        # Memory usage (with gradual changes)
        self.memory_usage += random.uniform(-50, 50)
        self.memory_usage = max(100, min(2048, self.memory_usage))
        
        # Active connections
        change = random.randint(-5, 10)
        self.active_connections = max(0, self.active_connections + change)
        
        # Send metrics
        self.gauge('system.cpu_usage', self.cpu_usage)
        self.gauge('system.memory_usage_mb', self.memory_usage)
        self.gauge('system.active_connections', self.active_connections)
        
        # Disk I/O metrics
        self.increment('disk.reads', random.randint(0, 100))
        self.increment('disk.writes', random.randint(0, 50))
        
        # Network metrics
        self.histogram('network.bytes_in', random.randint(1024, 1048576))
        self.histogram('network.bytes_out', random.randint(512, 524288))

    def generate_business_metrics(self):
        """Generate business/application-specific metrics"""
        # User activity
        self.increment('users.login', random.randint(0, 5))
        self.increment('users.logout', random.randint(0, 3))
        self.gauge('users.active', random.randint(50, 500))
        
        # Database operations
        db_operations = ['select', 'insert', 'update', 'delete']
        for operation in db_operations:
            count = random.randint(0, 20)
            duration = random.uniform(0.001, 0.5)
            self.increment('database.operations', count, [f'operation:{operation}'])
            if count > 0:
                self.histogram('database.query_time', duration, [f'operation:{operation}'])
        
        # Cache metrics
        cache_hits = random.randint(80, 120)
        cache_misses = random.randint(5, 20)
        self.increment('cache.hits', cache_hits)
        self.increment('cache.misses', cache_misses)
        self.histogram('cache.hit_ratio', 
                      cache_hits / (cache_hits + cache_misses) * 100)
        
        # Queue metrics
        queue_size = random.randint(0, 100)
        processing_time = random.uniform(0.1, 5.0)
        self.gauge('queue.size', queue_size)
        self.histogram('queue.processing_time', processing_time)

    def generate_custom_metrics(self):
        """Generate custom application metrics with various types"""
        # Custom counters
        self.increment('custom.feature_usage', 1, ['feature:advanced_search'])
        self.increment('custom.api_calls', 1, ['version:v2', 'client:mobile'])
        
        # Custom gauges
        self.gauge('custom.worker_threads', random.randint(1, 20))
        self.gauge('custom.pending_jobs', random.randint(0, 50))
        
        # Custom histograms/timers
        self.histogram('custom.file_size_bytes', random.randint(1024, 10485760))
        self.timer('custom.process_duration_ms', random.randint(100, 5000))
        
        # Custom sets (simulate with counter)
        self.increment('custom.unique_visitors', 1, [f'user_id:user_{random.randint(1, 1000)}'])

    def run_metrics_generation(self):
        """Main metrics generation loop"""
        logger.info("Starting metrics generation...")
        
        iteration = 0
        while not self.stop_event.is_set():
            try:
                iteration += 1
                
                # Generate different types of metrics
                self.generate_web_metrics()
                self.generate_system_metrics()
                
                # Generate business metrics less frequently
                if iteration % 3 == 0:
                    self.generate_business_metrics()
                
                # Generate custom metrics even less frequently
                if iteration % 5 == 0:
                    self.generate_custom_metrics()
                
                # Log summary periodically
                if iteration % 10 == 0:
                    logger.info(f"Generated metrics batch {iteration} - "
                              f"Total requests: {self.request_count}, "
                              f"Errors: {self.error_count}, "
                              f"CPU: {self.cpu_usage:.1f}%, "
                              f"Memory: {self.memory_usage:.0f}MB")
                
                # Wait for next iteration
                if not self.stop_event.wait(self.metric_interval):
                    continue
                    
            except Exception as e:
                logger.error(f"Error generating metrics: {e}")
                if not self.stop_event.wait(5):  # Wait 5 seconds on error
                    continue

    def start(self):
        """Start the metrics generator"""
        logger.info("Starting DogStatsD metrics generator...")
        
        # Send initial heartbeat
        self.increment('app.startup')
        self.gauge('app.status', 1)  # 1 = running
        
        # Start metrics generation thread
        self.metrics_thread = Thread(target=self.run_metrics_generation)
        self.metrics_thread.daemon = True
        self.metrics_thread.start()
        
        logger.info("Metrics generator started successfully")

    def stop(self):
        """Stop the metrics generator"""
        logger.info("Stopping metrics generator...")
        
        # Signal stop
        self.stop_event.set()
        
        # Send shutdown metrics
        self.increment('app.shutdown')
        self.gauge('app.status', 0)  # 0 = stopped
        
        # Wait for thread to finish
        if self.metrics_thread and self.metrics_thread.is_alive():
            self.metrics_thread.join(timeout=5)
        
        logger.info("Metrics generator stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down...")
    if generator:
        generator.stop()
    sys.exit(0)

if __name__ == "__main__":
    # Global variable for signal handler
    generator = None
    
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Create and start generator
        generator = DogStatsDMetricsGenerator()
        generator.start()
        
        logger.info("Application started. Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if generator:
            generator.stop()