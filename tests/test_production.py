"""
Comprehensive test suite for production validation
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from api.main import app
from api.config import settings

client = TestClient(app)

# ==================== Health & Status ====================

class TestHealth:
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

# ==================== API Endpoints ====================

class TestAnalyzeEndpoint:
    def test_analyze_success(self):
        """Test successful analysis"""
        payload = {
            "description": "I have EC2 instances with RDS master-slave and API Gateway with Lambda functions",
            "provider": "openrouter",
            "model_id": "google/gemini-2.0-flash-exp:free"
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "failures" in data or "status" in data

    def test_analyze_short_description(self):
        """Test validation for short description"""
        payload = {
            "description": "Too short",
            "provider": "openrouter",
            "model_id": "google/gemini-2.0-flash-exp:free"
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 400

    def test_analyze_missing_description(self):
        """Test missing required field"""
        payload = {
            "provider": "openrouter",
            "model_id": "google/gemini-2.0-flash-exp:free"
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 422

    def test_analyze_long_description(self):
        """Test handling of very long description"""
        payload = {
            "description": "A" * 6000,  # Exceeds max
            "provider": "openrouter",
            "model_id": "google/gemini-2.0-flash-exp:free"
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 422

# ==================== Validation Endpoint ====================

class TestValidationEndpoint:
    def test_validate_valid_input(self):
        """Test validation of valid input"""
        payload = {
            "description": "This is a valid AWS architecture description with more than 10 characters"
        }
        response = client.post("/api/analyze/validate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert "length" in data

    def test_validate_short_input(self):
        """Test validation of short input"""
        payload = {
            "description": "Too short"
        }
        response = client.post("/api/analyze/validate", json=payload)
        assert response.status_code == 422

# ==================== Frontend Routes ====================

class TestFrontendRoutes:
    def test_index_page(self):
        """Test index page"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_analyze_page(self):
        """Test analyze page"""
        response = client.get("/analyze")
        assert response.status_code == 200

    def test_methodology_page(self):
        """Test methodology page"""
        response = client.get("/methodology")
        assert response.status_code == 200

    def test_settings_page(self):
        """Test settings page"""
        response = client.get("/settings")
        assert response.status_code == 200

# ==================== API Documentation ====================

class TestAPIDocumentation:
    def test_openapi_json(self):
        """Test OpenAPI schema generation"""
        response = client.get("/api/openapi.json")
        if settings.DEBUG:
            assert response.status_code == 200
            data = response.json()
            assert "openapi" in data
            assert "paths" in data
        else:
            assert response.status_code == 404

    def test_swagger_ui(self):
        """Test Swagger UI availability"""
        response = client.get("/api/docs")
        if settings.DEBUG:
            assert response.status_code == 200
        else:
            assert response.status_code == 404

    def test_redoc_ui(self):
        """Test ReDoc UI availability"""
        response = client.get("/api/redoc")
        if settings.DEBUG:
            assert response.status_code == 200
        else:
            assert response.status_code == 404

# ==================== Request Headers ====================

class TestRequestHeaders:
    def test_request_id_header(self):
        """Test that requests include X-Request-ID header"""
        response = client.get("/health")
        assert "x-request-id" in response.headers
        request_id = response.headers["x-request-id"]
        assert len(request_id) == 36  # UUID length

    def test_cors_headers(self):
        """Test CORS headers"""
        response = client.get("/health")
        assert "access-control-allow-origin" in response.headers

# ==================== Error Handling ====================

class TestErrorHandling:
    def test_404_not_found(self):
        """Test 404 error"""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test method not allowed"""
        response = client.get("/api/analyze")
        assert response.status_code == 405

# ==================== Performance ====================

class TestPerformance:
    def test_response_time_health(self):
        """Test health endpoint response time"""
        import time
        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start
        assert elapsed < 0.1  # Should be < 100ms
        assert response.status_code == 200

# ==================== Configuration ====================

class TestConfiguration:
    def test_settings_loaded(self):
        """Test that settings are loaded"""
        assert settings.ENVIRONMENT is not None
        assert settings.PORT > 0
        assert settings.HOST is not None

    def test_debug_mode(self):
        """Test debug mode detection"""
        assert isinstance(settings.DEBUG, bool)

# ==================== Integration Tests ====================

class TestIntegration:
    @pytest.mark.integration
    def test_full_analysis_flow(self):
        """Test complete analysis flow"""
        # 1. Check health
        health = client.get("/health")
        assert health.status_code == 200

        # 2. Validate input
        validation = client.post("/api/analyze/validate", json={
            "description": "EC2 with single RDS instance and API Gateway"
        })
        assert validation.status_code == 200

        # 3. Perform analysis
        analysis = client.post("/api/analyze", json={
            "description": "EC2 with single RDS instance and API Gateway with Lambda functions"
        })
        assert analysis.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
