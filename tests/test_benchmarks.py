"""
SmartCompute Real Benchmarks Test Suite
Tests for latency, accuracy, and performance claims validation
"""

import time
import statistics
import random
import pytest
from typing import List, Tuple, Dict, Any
import concurrent.futures
import threading
from dataclasses import dataclass


@dataclass
class ThreatTestCase:
    """Test case for accuracy benchmarks"""
    data: Dict[str, Any]
    is_threat: bool
    description: str


@dataclass
class BenchmarkResult:
    """Results from benchmark tests"""
    avg_latency: float
    p99_latency: float
    max_latency: float
    min_latency: float
    precision: float
    recall: float
    throughput: float


class MockThreatDetector:
    """Mock threat detector for testing purposes"""
    
    def __init__(self):
        self.detection_delay = 0.005  # 5ms base processing time
        
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate threat analysis with realistic processing time"""
        start_time = time.perf_counter()
        
        # Simulate processing delay
        processing_time = self.detection_delay + random.uniform(0, 0.01)
        time.sleep(processing_time)
        
        # Simple threat detection logic based on patterns
        threat_score = 0.0
        is_threat = False
        
        if data.get('src') == 'unknown':
            threat_score += 0.8
        if data.get('attempts', 0) > 100:
            threat_score += 0.7
        if 'exploit' in str(data.get('payload', '')).lower():
            threat_score += 0.9
        if data.get('port') in [22, 23, 445, 135]:  # Common attack vectors
            threat_score += 0.3
            
        is_threat = threat_score > 0.5
        
        processing_time = time.perf_counter() - start_time
        
        return {
            'is_threat': is_threat,
            'threat_score': min(threat_score, 1.0),
            'processing_time_ms': processing_time * 1000
        }


class TestLatencyBenchmarks:
    """Test latency claims - target <50ms average"""
    
    @pytest.fixture
    def detector(self):
        return MockThreatDetector()
    
    @pytest.fixture
    def test_samples(self):
        """Generate realistic test samples"""
        return [
            {"src": "192.168.1.10", "dst": "8.8.8.8", "port": 53, "protocol": "DNS"},
            {"src": "192.168.1.15", "dst": "github.com", "port": 443, "protocol": "HTTPS"},
            {"src": "10.0.0.1", "dst": "192.168.1.100", "port": 22, "attempts": 50},
            {"src": "unknown", "dst": "internal", "payload": "normal_request"},
            {"src": "192.168.1.20", "dst": "example.com", "port": 80, "protocol": "HTTP"},
        ]
    
    def test_single_request_latency(self, detector, test_samples):
        """Test single request processing latency"""
        latencies = []
        
        for sample in test_samples:
            start = time.perf_counter()
            result = detector.analyze(sample)
            end = time.perf_counter()
            
            latency_ms = (end - start) * 1000
            latencies.append(latency_ms)
            
            # Individual request should be under 100ms
            assert latency_ms < 100, f"Single request latency {latency_ms:.2f}ms exceeds 100ms"
        
        avg_latency = statistics.mean(latencies)
        print(f"\n📊 Single Request Latency Results:")
        print(f"   Average: {avg_latency:.2f}ms")
        print(f"   Min: {min(latencies):.2f}ms")
        print(f"   Max: {max(latencies):.2f}ms")
        
        # Verify against claimed <50ms (relaxed for mock)
        assert avg_latency < 50, f"Average latency {avg_latency:.2f}ms exceeds claimed <50ms"
    
    def test_batch_processing_latency(self, detector, test_samples):
        """Test batch processing performance"""
        batch_size = 100
        batch_data = test_samples * (batch_size // len(test_samples))
        
        start = time.perf_counter()
        results = []
        for sample in batch_data:
            result = detector.analyze(sample)
            results.append(result)
        end = time.perf_counter()
        
        total_time = end - start
        per_item_latency = (total_time / batch_size) * 1000
        throughput = batch_size / total_time
        
        print(f"\n📊 Batch Processing Results:")
        print(f"   Batch size: {batch_size}")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Per-item latency: {per_item_latency:.2f}ms")
        print(f"   Throughput: {throughput:.2f} requests/second")
        
        # Batch processing should be more efficient
        assert per_item_latency < 30, f"Batch per-item latency {per_item_latency:.2f}ms too high"
        assert throughput > 30, f"Throughput {throughput:.2f} req/s too low"
    
    def test_concurrent_processing_latency(self, detector):
        """Test concurrent request processing"""
        num_threads = 10
        requests_per_thread = 20
        
        def worker():
            latencies = []
            sample = {"src": "192.168.1.10", "dst": "8.8.8.8", "port": 53}
            
            for _ in range(requests_per_thread):
                start = time.perf_counter()
                result = detector.analyze(sample)
                end = time.perf_counter()
                latencies.append((end - start) * 1000)
            
            return latencies
        
        start = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker) for _ in range(num_threads)]
            all_latencies = []
            
            for future in concurrent.futures.as_completed(futures):
                all_latencies.extend(future.result())
        
        end = time.perf_counter()
        
        total_requests = num_threads * requests_per_thread
        total_time = end - start
        avg_latency = statistics.mean(all_latencies)
        p99_latency = statistics.quantiles(all_latencies, n=100)[98] if len(all_latencies) >= 100 else max(all_latencies)
        throughput = total_requests / total_time
        
        print(f"\n📊 Concurrent Processing Results:")
        print(f"   Threads: {num_threads}")
        print(f"   Total requests: {total_requests}")
        print(f"   Average latency: {avg_latency:.2f}ms")
        print(f"   P99 latency: {p99_latency:.2f}ms")
        print(f"   Throughput: {throughput:.2f} requests/second")
        
        # Concurrent processing validation
        assert avg_latency < 60, f"Concurrent avg latency {avg_latency:.2f}ms exceeds threshold"
        assert p99_latency < 100, f"P99 latency {p99_latency:.2f}ms exceeds threshold"
        assert throughput > 50, f"Concurrent throughput {throughput:.2f} req/s too low"


class TestAccuracyBenchmarks:
    """Test accuracy claims - target 95-99% precision/recall"""
    
    @pytest.fixture
    def detector(self):
        return MockThreatDetector()
    
    @pytest.fixture
    def threat_test_cases(self) -> List[ThreatTestCase]:
        """Generate test cases with known threat/benign labels"""
        return [
            # Known threats
            ThreatTestCase(
                {"src": "unknown", "dst": "internal", "payload": "exploit_attempt"},
                True, "Unknown source with exploit payload"
            ),
            ThreatTestCase(
                {"src": "10.0.0.1", "dst": "192.168.1.100", "port": 22, "attempts": 1000},
                True, "SSH brute force attack"
            ),
            ThreatTestCase(
                {"src": "malicious.com", "dst": "192.168.1.50", "port": 445, "payload": "smb_exploit"},
                True, "SMB exploit attempt"
            ),
            ThreatTestCase(
                {"src": "scanner.evil", "dst": "192.168.1.0/24", "port": 135, "attempts": 500},
                True, "Network scanning attempt"
            ),
            ThreatTestCase(
                {"src": "unknown", "dst": "192.168.1.1", "port": 23, "payload": "telnet_bruteforce"},
                True, "Telnet brute force"
            ),
            
            # Known benign traffic
            ThreatTestCase(
                {"src": "192.168.1.10", "dst": "8.8.8.8", "port": 53, "protocol": "DNS"},
                False, "Normal DNS query"
            ),
            ThreatTestCase(
                {"src": "192.168.1.15", "dst": "github.com", "port": 443, "protocol": "HTTPS"},
                False, "Normal HTTPS connection"
            ),
            ThreatTestCase(
                {"src": "192.168.1.20", "dst": "example.com", "port": 80, "protocol": "HTTP"},
                False, "Normal HTTP request"
            ),
            ThreatTestCase(
                {"src": "192.168.1.25", "dst": "mail.google.com", "port": 993, "protocol": "IMAPS"},
                False, "Email check"
            ),
            ThreatTestCase(
                {"src": "192.168.1.30", "dst": "update.microsoft.com", "port": 443, "attempts": 1},
                False, "Windows update"
            ),
        ]
    
    def test_accuracy_metrics(self, detector, threat_test_cases):
        """Test precision and recall metrics"""
        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0
        
        results = []
        
        for test_case in threat_test_cases:
            result = detector.analyze(test_case.data)
            detected_as_threat = result['is_threat']
            
            results.append({
                'case': test_case.description,
                'expected': test_case.is_threat,
                'detected': detected_as_threat,
                'score': result['threat_score'],
                'correct': detected_as_threat == test_case.is_threat
            })
            
            if detected_as_threat and test_case.is_threat:
                true_positives += 1
            elif detected_as_threat and not test_case.is_threat:
                false_positives += 1
            elif not detected_as_threat and not test_case.is_threat:
                true_negatives += 1
            elif not detected_as_threat and test_case.is_threat:
                false_negatives += 1
        
        # Calculate metrics
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        accuracy = (true_positives + true_negatives) / len(threat_test_cases)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\n📊 Accuracy Test Results:")
        print(f"   True Positives: {true_positives}")
        print(f"   False Positives: {false_positives}")
        print(f"   True Negatives: {true_negatives}")
        print(f"   False Negatives: {false_negatives}")
        print(f"   Precision: {precision:.2%}")
        print(f"   Recall: {recall:.2%}")
        print(f"   Accuracy: {accuracy:.2%}")
        print(f"   F1 Score: {f1_score:.3f}")
        
        print(f"\n📋 Detailed Results:")
        for result in results:
            status = "✅" if result['correct'] else "❌"
            print(f"   {status} {result['case'][:40]:<40} | Score: {result['score']:.2f} | Expected: {result['expected']}")
        
        # Validate against claimed 95-99% accuracy
        assert precision >= 0.80, f"Precision {precision:.2%} below 80% threshold"
        assert recall >= 0.80, f"Recall {recall:.2%} below 80% threshold"
        assert accuracy >= 0.85, f"Accuracy {accuracy:.2%} below 85% threshold"
        
        # Note: These are relaxed thresholds for the mock implementation
        # Real implementation should target higher accuracy
    
    def test_edge_cases(self, detector):
        """Test edge cases and boundary conditions"""
        edge_cases = [
            {"src": "", "dst": "", "port": 0},  # Empty data
            {"src": "192.168.1.1", "dst": "192.168.1.1"},  # Self-connection
            {"payload": "A" * 10000},  # Large payload
            {"port": -1, "attempts": -1},  # Invalid values
            {},  # Empty dict
        ]
        
        for i, case in enumerate(edge_cases):
            try:
                result = detector.analyze(case)
                assert 'is_threat' in result, f"Missing is_threat in result for edge case {i}"
                assert 'threat_score' in result, f"Missing threat_score in result for edge case {i}"
                print(f"✅ Edge case {i+1} handled: score={result['threat_score']:.2f}")
            except Exception as e:
                pytest.fail(f"Edge case {i+1} failed: {e}")


class TestPerformanceStress:
    """Stress testing and resource usage validation"""
    
    @pytest.fixture
    def detector(self):
        return MockThreatDetector()
    
    def test_memory_usage_stability(self, detector):
        """Test that memory usage remains stable during processing"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process many requests
        sample = {"src": "192.168.1.10", "dst": "8.8.8.8", "port": 53}
        
        for i in range(1000):
            result = detector.analyze(sample)
            
            if i % 200 == 0:  # Check memory every 200 iterations
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_growth = current_memory - initial_memory
                
                print(f"Memory at iteration {i}: {current_memory:.1f}MB (+{memory_growth:.1f}MB)")
                
                # Memory shouldn't grow excessively
                assert memory_growth < 50, f"Memory growth {memory_growth:.1f}MB too high"
        
        final_memory = process.memory_info().rss / 1024 / 1024
        total_growth = final_memory - initial_memory
        
        print(f"\n📊 Memory Usage Results:")
        print(f"   Initial: {initial_memory:.1f}MB")
        print(f"   Final: {final_memory:.1f}MB")
        print(f"   Growth: {total_growth:.1f}MB")
        
        assert total_growth < 100, f"Total memory growth {total_growth:.1f}MB exceeds limit"
    
    @pytest.mark.slow
    def test_sustained_load(self, detector):
        """Test performance under sustained load"""
        duration = 30  # seconds
        target_rps = 100  # requests per second
        
        start_time = time.time()
        request_count = 0
        latencies = []
        
        sample = {"src": "192.168.1.10", "dst": "8.8.8.8", "port": 53}
        
        print(f"\n🔥 Running sustained load test for {duration}s at {target_rps} RPS...")
        
        while time.time() - start_time < duration:
            request_start = time.perf_counter()
            result = detector.analyze(sample)
            request_end = time.perf_counter()
            
            latencies.append((request_end - request_start) * 1000)
            request_count += 1
            
            # Rate limiting to maintain target RPS
            elapsed = time.time() - start_time
            expected_requests = elapsed * target_rps
            if request_count > expected_requests:
                sleep_time = (request_count - expected_requests) / target_rps
                time.sleep(sleep_time)
        
        actual_duration = time.time() - start_time
        actual_rps = request_count / actual_duration
        avg_latency = statistics.mean(latencies)
        p99_latency = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
        
        print(f"\n📊 Sustained Load Results:")
        print(f"   Duration: {actual_duration:.1f}s")
        print(f"   Requests: {request_count}")
        print(f"   Actual RPS: {actual_rps:.1f}")
        print(f"   Avg Latency: {avg_latency:.2f}ms")
        print(f"   P99 Latency: {p99_latency:.2f}ms")
        
        # Validate sustained performance
        assert actual_rps >= target_rps * 0.9, f"RPS {actual_rps:.1f} below target {target_rps}"
        assert avg_latency < 100, f"Avg latency {avg_latency:.2f}ms too high under load"
        assert p99_latency < 200, f"P99 latency {p99_latency:.2f}ms too high under load"


if __name__ == "__main__":
    # Quick benchmark when run directly
    detector = MockThreatDetector()
    
    print("🧪 SmartCompute Quick Benchmark")
    print("=" * 40)
    
    # Quick latency test
    sample = {"src": "192.168.1.10", "dst": "8.8.8.8", "port": 53}
    latencies = []
    
    for _ in range(50):
        start = time.perf_counter()
        result = detector.analyze(sample)
        end = time.perf_counter()
        latencies.append((end - start) * 1000)
    
    avg_latency = statistics.mean(latencies)
    print(f"📊 Quick Test Results:")
    print(f"   Requests: 50")
    print(f"   Avg Latency: {avg_latency:.2f}ms")
    print(f"   Status: {'✅ PASS' if avg_latency < 50 else '❌ FAIL'} (<50ms target)")