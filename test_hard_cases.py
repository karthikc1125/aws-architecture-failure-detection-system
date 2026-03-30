"""
Comprehensive hard test cases for the two-part analysis system
Tests edge cases, performance, and production readiness
"""
import requests
import json
import time
import concurrent.futures
from typing import List, Dict, Tuple
import pytest

BASE_URL = "http://localhost:8000/api"

# ============================================================================
# TEST DATA - Hard Cases
# ============================================================================

EDGE_CASE_TESTS = {
    "minimal_input": "web app",
    "very_long_input": "A" * 4500,  # Near max
    "special_chars": "Web app with <script>alert('xss')</script> and 'sql injection'",
    "unicode_emoji": "🚀 Cloud ☁️ Architecture 🏗️ with émojis",
    "sql_injection": "'; DROP TABLE architecture; --",
    "html_injection": "<h1>Injected</h1>",
    "null_bytes": "test\x00injection",
    "only_spaces": "     ",
    "mixed_case": "wEb ApP WiTh MiXeD cAsE",
    "numbers_only": "12345",
    "special_symbols": "!@#$%^&*()",
}

COMPLEX_ARCHITECTURES = {
    "simple_web": "Simple web app with 1 server",
    "microservices": "Microservices architecture with 15+ services, distributed across 3 regions, using ECS, RDS, ElastiCache, SNS/SQS",
    "data_heavy": "Real-time data pipeline processing 10TB/day, using Kinesis, Lambda, S3, Athena, Redshift with cross-region replication",
    "high_availability": "Multi-AZ RDS with read replicas, ALB, Auto Scaling Groups, Lambda concurrent execution limits, Circuit breakers",
    "compliance_heavy": "HIPAA/PCI-DSS compliant with encryption at rest/transit, VPC endpoints, PrivateLink, CloudHSM, KMS",
    "global_scale": "Global CDN with CloudFront, Route53 geolocation routing, multi-region failover, 500K requests/sec",
    "iot_scale": "IoT platform with 1M concurrent devices, Greengrass, IoT Core, timestream, DynamoDB streams",
    "ml_pipeline": "ML training pipeline with SageMaker, EC2 GPU instances, S3 for data, Lambda for orchestration, cost optimization",
    "serverless_heavy": "100% serverless: Lambda, DynamoDB, API Gateway, Cognito, Step Functions, EventBridge",
    "hybrid_complex": "Hybrid cloud with on-premise databases, AWS Direct Connect, VPN, DataSync, Storage Gateway",
}

PERFORMANCE_TESTS = [
    ("bulk_small_requests", [COMPLEX_ARCHITECTURES["simple_web"]] * 10),
    ("bulk_large_requests", [COMPLEX_ARCHITECTURES["data_heavy"]] * 5),
    ("mixed_size_requests", [
        COMPLEX_ARCHITECTURES["simple_web"],
        COMPLEX_ARCHITECTURES["microservices"],
        COMPLEX_ARCHITECTURES["data_heavy"],
    ] * 3),
]

# ============================================================================
# DEPLOYED ENDPOINT TESTS
# ============================================================================

class TestDeployedEndpoint:
    """Hard test cases for /api/analyze/deployed endpoint"""

    def test_deployed_minimum_valid_input(self):
        """Test with minimum valid input"""
        data = {"description": "simple web"}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200
        result = response.json()
        assert "status" in result
        assert result["status"] in ["optimized", "analyzed"]
        assert "analysis_type" in result

    def test_deployed_maximum_valid_input(self):
        """Test with maximum valid input (4950 chars)"""
        data = {"description": "A" * 4950}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200
        result = response.json()
        assert "status" in result

    def test_deployed_just_under_limit(self):
        """Test input just under 5000 char limit"""
        data = {"description": "Web app " + "x" * 4993}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200

    def test_deployed_exact_10_chars(self):
        """Test with exactly 10 characters (minimum)"""
        data = {"description": "1234567890"}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200

    def test_deployed_with_special_chars(self):
        """Test with special characters that are safe"""
        data = {"description": "Web app with (parentheses), [brackets], {braces} and \"quotes\""}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200

    def test_deployed_with_xss_attempt(self):
        """Test XSS injection attempt is handled"""
        data = {"description": "Web app <script>alert('xss')</script> security test"}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        # Should either return 200 (content escaped) or 422 (invalid)
        assert response.status_code in [200, 422]

    def test_deployed_with_sql_injection(self):
        """Test SQL injection attempt is handled"""
        data = {"description": "Web app '; DROP TABLE; --' test"}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code in [200, 422]

    def test_deployed_with_unicode_emoji(self):
        """Test with unicode and emoji characters"""
        data = {"description": "🚀 App in 中文 with émojis and spëcial chars"}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200

    def test_deployed_with_newlines_tabs(self):
        """Test with newlines and tabs"""
        data = {"description": "Web app\nwith\nnewlines\tand\ttabs\tincluded"}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200

    def test_deployed_complex_architecture(self):
        """Test with complex real-world architecture"""
        data = {"description": COMPLEX_ARCHITECTURES["microservices"]}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200
        result = response.json()
        assert "quick_wins" in result or "issues" in result

    def test_deployed_data_heavy_system(self):
        """Test with data-heavy pipeline"""
        data = {"description": COMPLEX_ARCHITECTURES["data_heavy"]}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200

    def test_deployed_compliance_heavy(self):
        """Test with compliance requirements"""
        data = {"description": COMPLEX_ARCHITECTURES["compliance_heavy"]}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200

    def test_deployed_global_scale(self):
        """Test with global scale requirements"""
        data = {"description": COMPLEX_ARCHITECTURES["global_scale"]}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200

    def test_deployed_iot_scale(self):
        """Test with IoT scale"""
        data = {"description": COMPLEX_ARCHITECTURES["iot_scale"]}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200

    def test_deployed_response_structure(self):
        """Test response has all required fields"""
        data = {"description": "Multi-AZ RDS with read replicas and ALB"}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200
        result = response.json()
        
        required_fields = ["status", "analysis_type"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

    def test_deployed_cost_estimates(self):
        """Test that cost optimization recommendations are provided"""
        data = {"description": "Single large EC2 instance running everything"}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200
        result = response.json()
        assert "quick_wins" in result or "total_potential_savings" in result


# ============================================================================
# FRESH ENDPOINT TESTS
# ============================================================================

class TestFreshEndpoint:
    """Hard test cases for /api/analyze/fresh endpoint"""

    def test_fresh_minimum_valid_input(self):
        """Test with minimum valid input"""
        data = {"description": "web server"}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200
        result = response.json()
        assert "status" in result
        assert result["status"] in ["designed", "created"]

    def test_fresh_maximum_valid_input(self):
        """Test with maximum valid input"""
        data = {"description": "B" * 4950}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200

    def test_fresh_exact_10_chars(self):
        """Test with exactly 10 characters"""
        data = {"description": "web service"}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200

    def test_fresh_web_app_detection(self):
        """Test web app workload detection"""
        data = {"description": "Build a web application with user authentication"}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200
        result = response.json()
        assert "recommended_architecture" in result or "project_type" in result

    def test_fresh_mobile_app_detection(self):
        """Test mobile app backend workload detection"""
        data = {"description": "Mobile app backend API for iOS and Android"}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200

    def test_fresh_data_heavy_detection(self):
        """Test data-heavy workload detection"""
        data = {"description": "Build data lake for analytics processing petabytes"}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200

    def test_fresh_real_time_detection(self):
        """Test real-time workload detection"""
        data = {"description": "Real-time streaming analytics for IoT sensors"}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200

    def test_fresh_simple_workload_detection(self):
        """Test simple workload detection"""
        data = {"description": "Static website hosting"}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200

    def test_fresh_response_structure(self):
        """Test response has all required fields"""
        data = {"description": "Build high-availability web application"}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200
        result = response.json()
        
        required_fields = ["status", "design_type", "recommended_architecture", "estimated_cost"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

    def test_fresh_cost_estimation(self):
        """Test cost estimation is provided"""
        data = {"description": "Serverless application architecture"}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200
        result = response.json()
        assert "estimated_cost" in result or "estimated_monthly_cost" in result

    def test_fresh_scalability_path(self):
        """Test scalability path is provided"""
        data = {"description": "E-commerce platform for 1000 concurrent users"}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200
        result = response.json()
        assert "scalability_path" in result or "implementation_phase" in result

    def test_fresh_ml_workload(self):
        """Test ML workload detection"""
        data = {"description": "ML model training and inference pipeline"}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200

    def test_fresh_iot_workload(self):
        """Test IoT workload detection"""
        data = {"description": "IoT platform for managing 100K edge devices"}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and validation"""

    def test_too_short_deployed(self):
        """Test deployed endpoint rejects too short input"""
        data = {"description": "123"}  # Less than 10 chars
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 422

    def test_too_short_fresh(self):
        """Test fresh endpoint rejects too short input"""
        data = {"description": "abc"}  # Less than 10 chars
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 422

    def test_too_long_deployed(self):
        """Test deployed endpoint rejects too long input"""
        data = {"description": "X" * 5001}  # More than 5000 chars
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 422

    def test_too_long_fresh(self):
        """Test fresh endpoint rejects too long input"""
        data = {"description": "Y" * 5001}  # More than 5000 chars
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 422

    def test_missing_description_deployed(self):
        """Test missing description field"""
        data = {}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 422

    def test_missing_description_fresh(self):
        """Test missing description field"""
        data = {}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 422

    def test_null_description_deployed(self):
        """Test null description"""
        data = {"description": None}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 422

    def test_empty_string_deployed(self):
        """Test empty string"""
        data = {"description": ""}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 422

    def test_only_whitespace_deployed(self):
        """Test only whitespace"""
        data = {"description": "    \n\t    "}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        # Should be rejected or trimmed to empty
        assert response.status_code in [422, 200]


# ============================================================================
# PERFORMANCE & LOAD TESTS
# ============================================================================

class TestPerformance:
    """Performance and load testing"""

    def test_response_time_deployed_simple(self):
        """Test response time for simple input"""
        data = {"description": "Simple web application"}
        start = time.time()
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 10, f"Response took {elapsed}s (should be < 10s)"

    def test_response_time_fresh_simple(self):
        """Test response time for simple input"""
        data = {"description": "Simple web application"}
        start = time.time()
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 10, f"Response took {elapsed}s (should be < 10s)"

    def test_response_time_deployed_complex(self):
        """Test response time for complex input"""
        data = {"description": COMPLEX_ARCHITECTURES["microservices"]}
        start = time.time()
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 15, f"Complex response took {elapsed}s (should be < 15s)"

    def test_concurrent_deployed_requests(self):
        """Test concurrent requests to deployed endpoint"""
        def make_request(desc):
            data = {"description": desc}
            return requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(make_request, desc)
                for desc in [COMPLEX_ARCHITECTURES["simple_web"]] * 5
            ]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in results)

    def test_concurrent_fresh_requests(self):
        """Test concurrent requests to fresh endpoint"""
        def make_request(desc):
            data = {"description": desc}
            return requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(make_request, desc)
                for desc in [COMPLEX_ARCHITECTURES["simple_web"]] * 5
            ]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        assert all(r.status_code == 200 for r in results)

    def test_sequential_stress_deployed(self):
        """Stress test with sequential requests"""
        for i in range(20):
            data = {"description": f"Test architecture {i} with web server and database"}
            response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
            assert response.status_code == 200

    def test_sequential_stress_fresh(self):
        """Stress test with sequential requests"""
        for i in range(20):
            data = {"description": f"Test project {i} for web application"}
            response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
            assert response.status_code == 200


# ============================================================================
# CONSISTENCY TESTS
# ============================================================================

class TestConsistency:
    """Test consistency of responses"""

    def test_deployed_response_consistency(self):
        """Test that same input gives consistent response structure"""
        data = {"description": "Multi-tier web application with database"}
        
        response1 = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        response2 = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        result1 = response1.json()
        result2 = response2.json()
        
        # Same structure should be returned
        assert set(result1.keys()) == set(result2.keys())

    def test_fresh_response_consistency(self):
        """Test that same input gives consistent response structure"""
        data = {"description": "Build a web application"}
        
        response1 = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        response2 = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        result1 = response1.json()
        result2 = response2.json()
        
        # Same structure should be returned
        assert set(result1.keys()) == set(result2.keys())


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class TestValidation:
    """Test input validation"""

    def test_deployed_with_very_long_description(self):
        """Test with very long but valid description"""
        long_desc = "Web application " + "with components " * 300
        data = {"description": long_desc[:5000]}  # Ensure within limit
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200

    def test_fresh_with_very_long_description(self):
        """Test with very long but valid description"""
        long_desc = "Build project " + "with features " * 300
        data = {"description": long_desc[:5000]}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200

    def test_deployed_response_is_json(self):
        """Verify response is valid JSON"""
        data = {"description": "Test web application"}
        response = requests.post(f"{BASE_URL}/analyze/deployed", json=data)
        assert response.status_code == 200
        # Should not raise
        result = response.json()
        assert isinstance(result, dict)

    def test_fresh_response_is_json(self):
        """Verify response is valid JSON"""
        data = {"description": "Test project"}
        response = requests.post(f"{BASE_URL}/analyze/fresh", json=data)
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, dict)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for the two-part system"""

    def test_both_endpoints_same_input(self):
        """Test both endpoints with same input"""
        description = "Multi-tier web application with microservices"
        
        deployed_data = {"description": description}
        fresh_data = {"description": description}
        
        deployed_response = requests.post(f"{BASE_URL}/analyze/deployed", json=deployed_data)
        fresh_response = requests.post(f"{BASE_URL}/analyze/fresh", json=fresh_data)
        
        assert deployed_response.status_code == 200
        assert fresh_response.status_code == 200
        
        deployed_result = deployed_response.json()
        fresh_result = fresh_response.json()
        
        # Both should return analysis
        assert "status" in deployed_result
        assert "status" in fresh_result

    def test_workflow_deployed_to_fresh(self):
        """Test workflow from deployed analysis to fresh design"""
        # First analyze a deployed system
        deployed_data = {"description": "Current: Single large EC2 instance"}
        deployed_response = requests.post(f"{BASE_URL}/analyze/deployed", json=deployed_data)
        assert deployed_response.status_code == 200
        
        # Then design a fresh system with recommendations
        fresh_data = {"description": "New project: Web application with high availability"}
        fresh_response = requests.post(f"{BASE_URL}/analyze/fresh", json=fresh_data)
        assert fresh_response.status_code == 200


if __name__ == "__main__":
    print("Running hard test cases...")
    print("Make sure the server is running on http://localhost:8000")
    print()
    
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])
