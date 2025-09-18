#!/usr/bin/env python3
"""
SmartCompute Enterprise - XDR Coordination Performance Benchmarks

Comprehensive performance testing suite for XDR coordination including:
- Latency measurement for multi-platform exports
- Throughput testing for bulk threat data processing
- Response time analysis for coordinated actions
- Resource utilization monitoring
- Load testing for concurrent threat scenarios
"""

import asyncio
import time
import logging
import statistics
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import psutil
import resource

# Add the enterprise directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xdr_mcp_coordinators import (
    CrowdStrikeCoordinator,
    SentinelCoordinator,
    CiscoUmbrellaCoordinator,
    XDRExportTask,
    XDRPlatform,
    ExportPriority
)
from multi_xdr_response_engine import MultiXDRResponseEngine
from business_context_xdr_router import BusinessContextXDRRouter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Métrica de rendimiento"""
    operation: str
    platform: str
    latency_ms: float
    throughput_ops_per_sec: float
    memory_usage_mb: float
    cpu_usage_percent: float
    success_rate: float
    error_count: int
    timestamp: datetime

@dataclass
class BenchmarkResults:
    """Resultados de benchmark"""
    test_name: str
    total_operations: int
    duration_seconds: float
    avg_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_ops_per_sec: float
    success_rate: float
    memory_peak_mb: float
    cpu_avg_percent: float
    errors: List[str]
    metrics: List[PerformanceMetric]

class XDRPerformanceBenchmark:
    """Benchmark de rendimiento para coordinación XDR"""

    def __init__(self):
        self.config = {
            "simulation_mode": True,
            "api_base": "https://benchmark.test.com",
            "timeout_seconds": 30
        }

        self.coordinators = {
            "crowdstrike": CrowdStrikeCoordinator(self.config),
            "sentinel": SentinelCoordinator(self.config),
            "umbrella": CiscoUmbrellaCoordinator(self.config)
        }

        self.response_engine = MultiXDRResponseEngine(self.config)
        self.router = BusinessContextXDRRouter(self.config)

        self.metrics: List[PerformanceMetric] = []
        self.errors: List[str] = []

    async def setup_coordinators(self):
        """Configurar y autenticar coordinadores"""
        logger.info("🔧 Setting up XDR coordinators...")

        for name, coordinator in self.coordinators.items():
            try:
                success = await coordinator.authenticate()
                if success:
                    logger.info(f"✅ {name.title()} coordinator authenticated")
                else:
                    logger.warning(f"⚠️ {name.title()} coordinator authentication failed")
            except Exception as e:
                logger.error(f"❌ {name.title()} coordinator setup error: {e}")

    def generate_test_threats(self, count: int) -> List[XDRExportTask]:
        """Generar amenazas de prueba"""
        threats = []

        threat_types = ["malware", "phishing", "apt", "ransomware", "insider_threat"]
        business_units = ["finance", "hr", "engineering", "executive", "operations"]
        priorities = list(ExportPriority)

        for i in range(count):
            threat = XDRExportTask(
                task_id=f"benchmark_threat_{i:06d}",
                platform=XDRPlatform.CROWDSTRIKE,  # Will be distributed later
                threat_data={
                    "indicator": f"192.168.{i//256}.{i%256}",
                    "type": "ip",
                    "threat_type": threat_types[i % len(threat_types)],
                    "severity": "high" if i % 3 == 0 else "medium",
                    "first_seen": datetime.utcnow().isoformat(),
                    "last_seen": datetime.utcnow().isoformat()
                },
                hrm_analysis={
                    "hrm_analysis": {
                        "final_assessment": {
                            "confidence": 0.7 + (i % 30) / 100,
                            "threat_level": "HIGH" if i % 4 == 0 else "MEDIUM",
                            "risk_score": 70 + (i % 30)
                        }
                    }
                },
                business_context={
                    "business_unit": business_units[i % len(business_units)],
                    "compliance_frameworks": ["SOX"] if i % 5 == 0 else [],
                    "criticality": "high" if i % 6 == 0 else "medium"
                },
                priority=priorities[i % len(priorities)],
                export_format="stix"
            )
            threats.append(threat)

        return threats

    async def benchmark_single_export_latency(self, iterations: int = 100) -> BenchmarkResults:
        """Benchmark de latencia para exportación individual"""
        logger.info(f"🚀 Starting single export latency benchmark ({iterations} iterations)")

        start_time = time.time()
        latencies = []
        errors = []
        success_count = 0

        # Monitor resource usage
        process = psutil.Process()
        memory_usage = []
        cpu_usage = []

        for i in range(iterations):
            # Generate single threat
            threat = self.generate_test_threats(1)[0]

            # Measure latency
            export_start = time.time()

            try:
                # Use CrowdStrike coordinator for single exports
                coordinator = self.coordinators["crowdstrike"]
                result = await coordinator.export_threat_data(threat)

                export_end = time.time()
                latency_ms = (export_end - export_start) * 1000

                if result.success:
                    latencies.append(latency_ms)
                    success_count += 1
                else:
                    errors.append(f"Export failed: {result.error_message}")

                # Collect resource metrics
                memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
                cpu_usage.append(process.cpu_percent())

                # Create performance metric
                metric = PerformanceMetric(
                    operation="single_export",
                    platform="crowdstrike",
                    latency_ms=latency_ms,
                    throughput_ops_per_sec=1 / (latency_ms / 1000) if latency_ms > 0 else 0,
                    memory_usage_mb=memory_usage[-1],
                    cpu_usage_percent=cpu_usage[-1],
                    success_rate=1 if result.success else 0,
                    error_count=0 if result.success else 1,
                    timestamp=datetime.now()
                )
                self.metrics.append(metric)

            except Exception as e:
                export_end = time.time()
                latency_ms = (export_end - export_start) * 1000
                errors.append(f"Exception: {str(e)}")
                logger.error(f"Export {i} failed: {e}")

        duration = time.time() - start_time

        # Calculate statistics
        if latencies:
            avg_latency = statistics.mean(latencies)
            median_latency = statistics.median(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
            p99_latency = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
        else:
            avg_latency = median_latency = p95_latency = p99_latency = 0

        results = BenchmarkResults(
            test_name="single_export_latency",
            total_operations=iterations,
            duration_seconds=duration,
            avg_latency_ms=avg_latency,
            median_latency_ms=median_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            throughput_ops_per_sec=success_count / duration if duration > 0 else 0,
            success_rate=success_count / iterations if iterations > 0 else 0,
            memory_peak_mb=max(memory_usage) if memory_usage else 0,
            cpu_avg_percent=statistics.mean(cpu_usage) if cpu_usage else 0,
            errors=errors,
            metrics=self.metrics[-iterations:]
        )

        logger.info(f"✅ Single export latency benchmark completed")
        return results

    async def benchmark_bulk_throughput(self, batch_size: int = 50, batches: int = 10) -> BenchmarkResults:
        """Benchmark de throughput para procesamiento en lote"""
        logger.info(f"🚀 Starting bulk throughput benchmark ({batches} batches of {batch_size})")

        start_time = time.time()
        total_operations = batch_size * batches
        success_count = 0
        errors = []
        all_latencies = []

        # Resource monitoring
        process = psutil.Process()
        memory_usage = []
        cpu_usage = []

        for batch_num in range(batches):
            batch_start = time.time()

            # Generate batch of threats
            threats = self.generate_test_threats(batch_size)

            # Distribute across platforms
            platform_batches = {
                "crowdstrike": [],
                "sentinel": [],
                "umbrella": []
            }

            for i, threat in enumerate(threats):
                platform_name = list(platform_batches.keys())[i % 3]
                platform_batches[platform_name].append(threat)

            # Process each platform batch concurrently
            batch_tasks = []
            for platform_name, platform_threats in platform_batches.items():
                if platform_threats:
                    coordinator = self.coordinators[platform_name]
                    for threat in platform_threats:
                        task = asyncio.create_task(coordinator.export_threat_data(threat))
                        batch_tasks.append((platform_name, task))

            # Wait for batch completion
            for platform_name, task in batch_tasks:
                try:
                    result = await task
                    batch_end = time.time()
                    latency_ms = (batch_end - batch_start) * 1000

                    if result.success:
                        success_count += 1
                        all_latencies.append(latency_ms)
                    else:
                        errors.append(f"Batch {batch_num} {platform_name} failed: {result.error_message}")

                except Exception as e:
                    errors.append(f"Batch {batch_num} {platform_name} exception: {str(e)}")

            # Collect resource metrics
            memory_usage.append(process.memory_info().rss / 1024 / 1024)
            cpu_usage.append(process.cpu_percent())

            # Log progress
            if (batch_num + 1) % 5 == 0:
                logger.info(f"  Completed {batch_num + 1}/{batches} batches")

        duration = time.time() - start_time

        # Calculate statistics
        if all_latencies:
            avg_latency = statistics.mean(all_latencies)
            median_latency = statistics.median(all_latencies)
            p95_latency = statistics.quantiles(all_latencies, n=20)[18] if len(all_latencies) >= 20 else max(all_latencies)
            p99_latency = statistics.quantiles(all_latencies, n=100)[98] if len(all_latencies) >= 100 else max(all_latencies)
        else:
            avg_latency = median_latency = p95_latency = p99_latency = 0

        results = BenchmarkResults(
            test_name="bulk_throughput",
            total_operations=total_operations,
            duration_seconds=duration,
            avg_latency_ms=avg_latency,
            median_latency_ms=median_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            throughput_ops_per_sec=success_count / duration if duration > 0 else 0,
            success_rate=success_count / total_operations if total_operations > 0 else 0,
            memory_peak_mb=max(memory_usage) if memory_usage else 0,
            cpu_avg_percent=statistics.mean(cpu_usage) if cpu_usage else 0,
            errors=errors[:10],  # Limit error list
            metrics=[]  # Skip individual metrics for bulk test
        )

        logger.info(f"✅ Bulk throughput benchmark completed")
        return results

    async def benchmark_coordinated_response(self, scenarios: int = 20) -> BenchmarkResults:
        """Benchmark de respuesta coordinada multi-XDR"""
        logger.info(f"🚀 Starting coordinated response benchmark ({scenarios} scenarios)")

        start_time = time.time()
        success_count = 0
        errors = []
        latencies = []

        # Resource monitoring
        process = psutil.Process()
        memory_usage = []
        cpu_usage = []

        for i in range(scenarios):
            scenario_start = time.time()

            # Generate threat scenario
            threat_data = {
                "threat_id": f"coordinated_test_{i:03d}",
                "source_ip": f"10.0.{i//256}.{i%256}",
                "threat_type": "apt" if i % 3 == 0 else "malware",
                "severity": "critical" if i % 4 == 0 else "high",
                "business_unit": "executive" if i % 5 == 0 else "finance",
                "compliance_frameworks": ["SOX", "PCI-DSS"] if i % 6 == 0 else ["SOX"]
            }

            # Define response plan
            response_plan = {
                "actions": [
                    {
                        "type": "block_ip",
                        "target": threat_data["source_ip"],
                        "platforms": ["crowdstrike", "sentinel", "umbrella"]
                    },
                    {
                        "type": "isolate_host",
                        "target": f"host_{i:03d}",
                        "platforms": ["crowdstrike", "sentinel"]
                    }
                ]
            }

            try:
                # Execute coordinated response
                result = await self.response_engine.execute_coordinated_response(threat_data, response_plan)

                scenario_end = time.time()
                latency_ms = (scenario_end - scenario_start) * 1000
                latencies.append(latency_ms)

                if result.get("success", False):
                    success_count += 1
                else:
                    errors.append(f"Scenario {i} failed: {result.get('error', 'Unknown error')}")

            except Exception as e:
                scenario_end = time.time()
                latency_ms = (scenario_end - scenario_start) * 1000
                latencies.append(latency_ms)
                errors.append(f"Scenario {i} exception: {str(e)}")

            # Collect resource metrics
            memory_usage.append(process.memory_info().rss / 1024 / 1024)
            cpu_usage.append(process.cpu_percent())

        duration = time.time() - start_time

        # Calculate statistics
        if latencies:
            avg_latency = statistics.mean(latencies)
            median_latency = statistics.median(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
            p99_latency = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
        else:
            avg_latency = median_latency = p95_latency = p99_latency = 0

        results = BenchmarkResults(
            test_name="coordinated_response",
            total_operations=scenarios,
            duration_seconds=duration,
            avg_latency_ms=avg_latency,
            median_latency_ms=median_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            throughput_ops_per_sec=success_count / duration if duration > 0 else 0,
            success_rate=success_count / scenarios if scenarios > 0 else 0,
            memory_peak_mb=max(memory_usage) if memory_usage else 0,
            cpu_avg_percent=statistics.mean(cpu_usage) if cpu_usage else 0,
            errors=errors[:10],
            metrics=[]
        )

        logger.info(f"✅ Coordinated response benchmark completed")
        return results

    async def benchmark_routing_performance(self, threats: int = 200) -> BenchmarkResults:
        """Benchmark de rendimiento del router de contexto de negocio"""
        logger.info(f"🚀 Starting routing performance benchmark ({threats} threats)")

        start_time = time.time()
        success_count = 0
        errors = []
        latencies = []

        for i in range(threats):
            routing_start = time.time()

            # Generate test threat for routing
            threat_context = {
                "threat_id": f"routing_test_{i:03d}",
                "threat_type": ["malware", "phishing", "apt", "ransomware"][i % 4],
                "severity": ["low", "medium", "high", "critical"][i % 4],
                "business_unit": ["finance", "hr", "engineering", "executive"][i % 4],
                "compliance_frameworks": [["SOX"], ["HIPAA"], ["PCI-DSS"], ["SOX", "PCI-DSS"]][i % 4],
                "region": ["us-east", "us-west", "eu-central", "ap-southeast"][i % 4]
            }

            try:
                # Determine optimal routing
                routing_result = self.router.determine_optimal_routing(threat_context)

                routing_end = time.time()
                latency_ms = (routing_end - routing_start) * 1000
                latencies.append(latency_ms)

                if routing_result and "primary_platforms" in routing_result:
                    success_count += 1
                else:
                    errors.append(f"Routing {i} failed: No primary platforms")

            except Exception as e:
                routing_end = time.time()
                latency_ms = (routing_end - routing_start) * 1000
                latencies.append(latency_ms)
                errors.append(f"Routing {i} exception: {str(e)}")

        duration = time.time() - start_time

        # Calculate statistics
        if latencies:
            avg_latency = statistics.mean(latencies)
            median_latency = statistics.median(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
            p99_latency = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
        else:
            avg_latency = median_latency = p95_latency = p99_latency = 0

        results = BenchmarkResults(
            test_name="routing_performance",
            total_operations=threats,
            duration_seconds=duration,
            avg_latency_ms=avg_latency,
            median_latency_ms=median_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            throughput_ops_per_sec=success_count / duration if duration > 0 else 0,
            success_rate=success_count / threats if threats > 0 else 0,
            memory_peak_mb=0,  # Routing is lightweight
            cpu_avg_percent=0,
            errors=errors[:10],
            metrics=[]
        )

        logger.info(f"✅ Routing performance benchmark completed")
        return results

    def print_benchmark_results(self, results: BenchmarkResults):
        """Imprimir resultados de benchmark"""
        print(f"\n📊 {results.test_name.upper()} BENCHMARK RESULTS")
        print("=" * 60)
        print(f"Total Operations: {results.total_operations:,}")
        print(f"Duration: {results.duration_seconds:.2f}s")
        print(f"Success Rate: {results.success_rate:.1%}")
        print(f"Throughput: {results.throughput_ops_per_sec:.1f} ops/sec")
        print()
        print("Latency Statistics:")
        print(f"  Average: {results.avg_latency_ms:.2f}ms")
        print(f"  Median: {results.median_latency_ms:.2f}ms")
        print(f"  95th percentile: {results.p95_latency_ms:.2f}ms")
        print(f"  99th percentile: {results.p99_latency_ms:.2f}ms")
        print()
        print("Resource Usage:")
        print(f"  Peak Memory: {results.memory_peak_mb:.1f}MB")
        print(f"  Average CPU: {results.cpu_avg_percent:.1f}%")

        if results.errors:
            print(f"\nErrors ({len(results.errors)} total):")
            for error in results.errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(results.errors) > 5:
                print(f"  ... and {len(results.errors) - 5} more")

    def save_benchmark_results(self, results: List[BenchmarkResults], filename: str = None):
        """Guardar resultados de benchmark a archivo JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"xdr_benchmark_results_{timestamp}.json"

        # Convert to JSON-serializable format
        json_results = []
        for result in results:
            json_result = asdict(result)
            # Remove metrics to reduce file size
            json_result["metrics"] = len(result.metrics)
            json_results.append(json_result)

        benchmark_data = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "platform": sys.platform,
                "python_version": sys.version,
                "cpu_count": os.cpu_count(),
                "memory_gb": psutil.virtual_memory().total / (1024**3)
            },
            "results": json_results
        }

        with open(filename, 'w') as f:
            json.dump(benchmark_data, f, indent=2)

        logger.info(f"💾 Benchmark results saved to {filename}")

async def run_comprehensive_benchmarks():
    """Ejecutar suite completa de benchmarks"""
    print("\n🏁 SmartCompute Enterprise - XDR Performance Benchmarks")
    print("=" * 65)

    benchmark = XDRPerformanceBenchmark()

    # Setup coordinators
    await benchmark.setup_coordinators()

    # Run all benchmarks
    all_results = []

    # 1. Single Export Latency
    logger.info("\n1️⃣ Running Single Export Latency Benchmark...")
    single_results = await benchmark.benchmark_single_export_latency(iterations=50)
    benchmark.print_benchmark_results(single_results)
    all_results.append(single_results)

    # 2. Bulk Throughput
    logger.info("\n2️⃣ Running Bulk Throughput Benchmark...")
    bulk_results = await benchmark.benchmark_bulk_throughput(batch_size=25, batches=5)
    benchmark.print_benchmark_results(bulk_results)
    all_results.append(bulk_results)

    # 3. Coordinated Response
    logger.info("\n3️⃣ Running Coordinated Response Benchmark...")
    response_results = await benchmark.benchmark_coordinated_response(scenarios=15)
    benchmark.print_benchmark_results(response_results)
    all_results.append(response_results)

    # 4. Routing Performance
    logger.info("\n4️⃣ Running Routing Performance Benchmark...")
    routing_results = await benchmark.benchmark_routing_performance(threats=100)
    benchmark.print_benchmark_results(routing_results)
    all_results.append(routing_results)

    # Save results
    benchmark.save_benchmark_results(all_results)

    # Overall summary
    print(f"\n🎯 OVERALL PERFORMANCE SUMMARY")
    print("=" * 40)
    total_ops = sum(r.total_operations for r in all_results)
    total_duration = sum(r.duration_seconds for r in all_results)
    avg_success_rate = statistics.mean([r.success_rate for r in all_results])

    print(f"Total Operations: {total_ops:,}")
    print(f"Total Duration: {total_duration:.1f}s")
    print(f"Average Success Rate: {avg_success_rate:.1%}")
    print(f"Overall Throughput: {total_ops / total_duration:.1f} ops/sec")

    print(f"\n✅ All benchmarks completed successfully!")

    return all_results

if __name__ == "__main__":
    # Run benchmarks
    results = asyncio.run(run_comprehensive_benchmarks())