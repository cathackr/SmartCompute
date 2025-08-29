"""
Tests for FastAPI endpoints
"""

import pytest
import json
from httpx import AsyncClient, ASGITransport
from app.api.main import app


class TestSmartComputeAPI:
    """Test SmartCompute API endpoints"""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
            
            data = response.json()
            assert "message" in data
            assert "version" in data
            assert "endpoints" in data
            assert data["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert "services" in data
    
    @pytest.mark.asyncio
    async def test_system_info(self):
        """Test system info endpoint"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/system-info")
            assert response.status_code == 200
            
            data = response.json()
            required_fields = [
                "os", "architecture", "cpu_model", 
                "cpu_cores", "ram_gb", "gpu_type"
            ]
            for field in required_fields:
                assert field in data
            
            assert data["cpu_cores"] > 0
            assert data["ram_gb"] > 0
    
    @pytest.mark.asyncio
    async def test_optimize_endpoint(self):
        """Test optimization endpoint"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "precision_needed": 0.95,
                "speed_priority": 0.5,
                "enable_verbose": False
            }
            
            response = await client.post("/optimize", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            required_fields = [
                "method", "time", "accuracy", "speedup",
                "meets_precision", "choice", "metrics"
            ]
            for field in required_fields:
                assert field in data
            
            assert data["time"] > 0
            assert 0 <= data["accuracy"] <= 1
            assert data["speedup"] > 0
            assert data["meets_precision"] is True
    
    @pytest.mark.asyncio
    async def test_optimize_with_different_parameters(self):
        """Test optimization with different parameters"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            test_cases = [
                {"precision_needed": 0.99, "speed_priority": 0.1},  # High precision
                {"precision_needed": 0.85, "speed_priority": 0.9},  # High speed
                {"precision_needed": 0.95, "speed_priority": 0.5}   # Balanced
            ]
            
            for params in test_cases:
                response = await client.post("/optimize", json=params)
                assert response.status_code == 200
                
                data = response.json()
                assert data["accuracy"] >= params["precision_needed"]
    
    @pytest.mark.asyncio
    async def test_establish_baseline(self):
        """Test baseline establishment endpoint"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {"duration": 10}  # Short duration for testing
            
            response = await client.post("/establish-baseline", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert "message" in data
            assert "baseline_metrics" in data
            assert "timestamp" in data
            
            metrics = data["baseline_metrics"]
            assert "cpu_mean" in metrics
            assert "memory_mean" in metrics
            assert metrics["cpu_mean"] >= 0
            assert metrics["memory_mean"] >= 0
    
    @pytest.mark.asyncio
    async def test_baseline_invalid_duration(self):
        """Test baseline establishment with invalid duration"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Too short duration
            response = await client.post("/establish-baseline", json={"duration": 5})
            assert response.status_code == 400
            
            # Too long duration
            response = await client.post("/establish-baseline", json={"duration": 500})
            assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_detect_anomalies_without_baseline(self):
        """Test anomaly detection without baseline"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/detect-anomalies")
            assert response.status_code == 400
            
            data = response.json()
            assert "No baseline established" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_detect_anomalies_with_baseline(self):
        """Test anomaly detection after establishing baseline"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # First establish baseline
            await client.post("/establish-baseline", json={"duration": 10})
            
            # Then detect anomalies
            response = await client.get("/detect-anomalies")
            assert response.status_code == 200
            
            data = response.json()
            required_fields = [
                "anomaly_score", "severity", "cpu_current",
                "memory_current", "timestamp"
            ]
            for field in required_fields:
                assert field in data
            
            assert 0 <= data["anomaly_score"] <= 100
            assert data["severity"] in ["normal", "low", "medium", "high"]
    
    @pytest.mark.asyncio
    async def test_performance_report(self):
        """Test performance report generation"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Establish baseline first
            await client.post("/establish-baseline", json={"duration": 10})
            
            # Generate report
            response = await client.get("/performance-report")
            assert response.status_code == 200
            
            data = response.json()
            required_sections = [
                "system_profile", "optimization_applied", 
                "security_status", "recommendations", "timestamp"
            ]
            for section in required_sections:
                assert section in data
            
            assert isinstance(data["recommendations"], list)
            assert len(data["recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_performance_history(self):
        """Test performance history endpoint"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Run some optimizations first
            await client.post("/optimize", json={"precision_needed": 0.95})
            await client.post("/optimize", json={"precision_needed": 0.90})
            
            # Get history
            response = await client.get("/performance-history")
            assert response.status_code == 200
            
            data = response.json()
            assert "total_operations" in data
            assert data["total_operations"] > 0
    
    @pytest.mark.asyncio
    async def test_monitoring_endpoints(self):
        """Test monitoring service endpoints"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Check initial status
            response = await client.get("/monitoring/status")
            assert response.status_code == 200
            
            status = response.json()
            assert "is_monitoring" in status
            assert status["is_monitoring"] is False
            
            # Start monitoring
            response = await client.post("/monitoring/start")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "active"
            
            # Check status after starting
            response = await client.get("/monitoring/status")
            assert response.status_code == 200
            
            status = response.json()
            assert status["is_monitoring"] is True
            
            # Stop monitoring
            response = await client.post("/monitoring/stop")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "inactive"
    
    @pytest.mark.asyncio
    async def test_invalid_optimization_parameters(self):
        """Test optimization endpoint with invalid parameters"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Invalid precision (> 1.0)
            response = await client.post("/optimize", json={
                "precision_needed": 1.5,
                "speed_priority": 0.5
            })
            # Should still work as the validation happens in the engine
            assert response.status_code == 200
            
            # Negative precision
            response = await client.post("/optimize", json={
                "precision_needed": -0.1,
                "speed_priority": 0.5
            })
            # Should still work as the validation happens in the engine
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import asyncio
        
        async def make_request(client):
            response = await client.post("/optimize", json={
                "precision_needed": 0.95,
                "speed_priority": 0.5,
                "enable_verbose": False
            })
            return response.status_code == 200
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Make multiple concurrent requests
            tasks = [make_request(client) for _ in range(3)]
            results = await asyncio.gather(*tasks)
            
            # All requests should succeed
            assert all(results)
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test API error handling"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Test invalid JSON
            response = await client.post(
                "/optimize",
                content="invalid json",
                headers={"content-type": "application/json"}
            )
            assert response.status_code == 422
            
            # Test missing required fields (should use defaults)
            response = await client.post("/optimize", json={})
            assert response.status_code == 200  # Should use defaults
    
    @pytest.mark.asyncio
    async def test_api_response_consistency(self):
        """Test that API responses are consistent"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Make the same request multiple times
            payload = {
                "precision_needed": 0.95,
                "speed_priority": 0.5,
                "enable_verbose": False
            }
            
            responses = []
            for _ in range(3):
                response = await client.post("/optimize", json=payload)
                assert response.status_code == 200
                responses.append(response.json())
            
            # All responses should have the same structure
            for response in responses:
                assert set(response.keys()) == set(responses[0].keys())
                
            # Results should be deterministic (same precision requirement)
            for response in responses:
                assert response["accuracy"] >= payload["precision_needed"]