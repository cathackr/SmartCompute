"""
Smoke tests for SmartCompute API
Basic functionality and health check validation
"""

import subprocess
import time
import requests
import pytest
from typing import Optional
import signal
import os


class APITestServer:
    """Context manager for API server during tests"""
    
    def __init__(self, port: int = 8000, timeout: int = 10):
        self.port = port
        self.timeout = timeout
        self.process: Optional[subprocess.Popen] = None
    
    def __enter__(self):
        """Start the API server"""
        self.process = subprocess.Popen(
            ['python3', 'main.py', '--api', '--port', str(self.port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # Create new process group
        )
        
        # Wait for server to start
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                response = requests.get(f'http://127.0.0.1:{self.port}/health', timeout=2)
                if response.status_code == 200:
                    return self
            except requests.exceptions.RequestException:
                pass
            time.sleep(0.5)
        
        # If we get here, server didn't start in time
        self.__exit__(None, None, None)
        raise RuntimeError(f"API server failed to start within {self.timeout} seconds")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the API server"""
        if self.process:
            try:
                # Send SIGTERM to the process group
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                # Force kill if graceful shutdown fails
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
            finally:
                self.process = None


def test_health_endpoint():
    """Test that the health endpoint returns successful response"""
    with APITestServer() as server:
        response = requests.get('http://127.0.0.1:8000/health', timeout=5)
        
        assert response.status_code == 200
        
        # Verify response structure
        health_data = response.json()
        assert 'status' in health_data
        assert health_data['status'] == 'healthy'


def test_health_endpoint_custom_port():
    """Test health endpoint on custom port"""
    test_port = 8001
    with APITestServer(port=test_port) as server:
        response = requests.get(f'http://127.0.0.1:{test_port}/health', timeout=5)
        
        assert response.status_code == 200
        health_data = response.json()
        assert health_data['status'] == 'healthy'


def test_api_docs_accessible():
    """Test that API documentation is accessible"""
    with APITestServer() as server:
        # Test OpenAPI docs
        docs_response = requests.get('http://127.0.0.1:8000/docs', timeout=5)
        assert docs_response.status_code == 200
        
        # Test OpenAPI JSON spec
        spec_response = requests.get('http://127.0.0.1:8000/openapi.json', timeout=5)
        assert spec_response.status_code == 200
        
        spec_data = spec_response.json()
        assert 'info' in spec_data
        assert spec_data['info']['title'] == 'SmartCompute API'


def test_server_startup_time():
    """Test that server starts within reasonable time"""
    start_time = time.time()
    
    with APITestServer(timeout=15) as server:
        startup_time = time.time() - start_time
        
        # Server should start within 10 seconds
        assert startup_time < 10, f"Server took too long to start: {startup_time:.2f}s"
        
        # Verify it's actually responding
        response = requests.get('http://127.0.0.1:8000/health', timeout=5)
        assert response.status_code == 200


def test_basic_api_functionality():
    """Test basic API endpoints beyond health"""
    with APITestServer() as server:
        # Test root endpoint
        root_response = requests.get('http://127.0.0.1:8000/', timeout=5)
        # Don't assert specific status, just that we get a response
        assert root_response.status_code in [200, 404, 422]  # Any valid HTTP response
        
        # Test health endpoint is working
        health_response = requests.get('http://127.0.0.1:8000/health', timeout=5)
        assert health_response.status_code == 200


@pytest.mark.slow
def test_server_stability():
    """Test server stability under basic load"""
    with APITestServer() as server:
        # Make multiple requests to ensure stability
        for i in range(10):
            response = requests.get('http://127.0.0.1:8000/health', timeout=5)
            assert response.status_code == 200, f"Request {i+1} failed"
            
            health_data = response.json()
            assert health_data['status'] == 'healthy'
            
            # Small delay between requests
            time.sleep(0.1)


if __name__ == "__main__":
    # Run basic smoke test when executed directly
    print("🧪 Running SmartCompute Smoke Test")
    print("=" * 40)
    
    try:
        test_health_endpoint()
        print("✅ Health endpoint test passed")
        
        test_api_docs_accessible()
        print("✅ API documentation test passed")
        
        test_server_startup_time()
        print("✅ Server startup time test passed")
        
        print("\n🎉 All smoke tests passed!")
        
    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}")
        exit(1)