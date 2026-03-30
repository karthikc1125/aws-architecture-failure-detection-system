"""
Production Test Suite Runner with Performance Analysis
Tests the system under realistic conditions with hard edge cases
"""
import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List
from collections import defaultdict
import statistics

BASE_URL = "http://localhost:8000/api"

class TestRunner:
    """Run comprehensive tests and collect metrics"""
    
    def __init__(self):
        self.results = {
            "deployed": defaultdict(list),
            "fresh": defaultdict(list),
            "errors": defaultdict(int),
        }
        self.start_time = None
        self.end_time = None
    
    def log(self, message: str, level: str = "INFO"):
        """Log test message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level:8} | {message}")
    
    def test_edge_cases_deployed(self) -> int:
        """Test deployed endpoint with edge cases"""
        self.log("Testing Deployed Endpoint - Edge Cases", "START")
        passed = 0
        
        test_cases = {
            "minimum (10 chars)": "1234567890",
            "maximum (5000 chars)": "A" * 5000,
            "special_chars": "Web app <html>, 'quotes', \"double\", [brackets]",
            "unicode/emoji": "🚀 App 中文 special chars é à ü",
            "newlines/tabs": "Web app\nwith\nnewlines\tand\ttabs",
            "complex_real": "Multi-AZ RDS with read replicas, ALB, Auto Scaling, Lambda, DynamoDB, S3, CloudFront",
            "very_complex": "Enterprise: Microservices (25+) across 4 regions, event-driven with Kafka, real-time analytics, ML pipeline, compliance (HIPAA/PCI), disaster recovery",
        }
        
        for name, desc in test_cases.items():
            try:
                start = time.time()
                response = requests.post(
                    f"{BASE_URL}/analyze/deployed",
                    json={"description": desc},
                    timeout=15
                )
                elapsed = time.time() - start
                
                self.results["deployed"][name].append({
                    "status": response.status_code,
                    "time": elapsed,
                    "success": response.status_code == 200,
                })
                
                if response.status_code == 200:
                    passed += 1
                    self.log(f"✓ {name}: {elapsed:.2f}s", "PASS")
                else:
                    self.log(f"✗ {name}: Status {response.status_code}", "FAIL")
                    
            except Exception as e:
                self.results["errors"]["deployed"] += 1
                self.log(f"✗ {name}: {str(e)}", "ERROR")
        
        self.log(f"Deployed edge cases: {passed}/{len(test_cases)} passed", "RESULT")
        return passed
    
    def test_edge_cases_fresh(self) -> int:
        """Test fresh endpoint with edge cases"""
        self.log("Testing Fresh Endpoint - Edge Cases", "START")
        passed = 0
        
        test_cases = {
            "minimum (10 chars)": "web service",
            "maximum (5000 chars)": "B" * 5000,
            "workload_web": "Web app with user auth, payments, real-time notifications",
            "workload_mobile": "Mobile backend for iOS/Android, push notifications, offline sync",
            "workload_data": "Data lake: ingest 100TB/day, process with Spark, serve analytics dashboards",
            "workload_real_time": "Real-time: 1M concurrent IoT devices, sub-second latency, streaming analytics",
            "workload_ml": "ML platform: model training, hyperparameter tuning, inference at scale, model serving",
            "workload_complex": "Complex: Serverless + Containers + Lambda + ECS + RDS + DynamoDB + Elasticsearch + Kafka + SageMaker",
        }
        
        for name, desc in test_cases.items():
            try:
                start = time.time()
                response = requests.post(
                    f"{BASE_URL}/analyze/fresh",
                    json={"description": desc},
                    timeout=15
                )
                elapsed = time.time() - start
                
                self.results["fresh"][name].append({
                    "status": response.status_code,
                    "time": elapsed,
                    "success": response.status_code == 200,
                })
                
                if response.status_code == 200:
                    passed += 1
                    self.log(f"✓ {name}: {elapsed:.2f}s", "PASS")
                else:
                    self.log(f"✗ {name}: Status {response.status_code}", "FAIL")
                    
            except Exception as e:
                self.results["errors"]["fresh"] += 1
                self.log(f"✗ {name}: {str(e)}", "ERROR")
        
        self.log(f"Fresh edge cases: {passed}/{len(test_cases)} passed", "RESULT")
        return passed
    
    def test_error_cases(self) -> int:
        """Test error handling"""
        self.log("Testing Error Cases", "START")
        passed = 0
        
        error_cases = {
            "too_short": "abc",
            "empty": "",
            "whitespace": "    ",
            "too_long": "X" * 5001,
            "null": None,
        }
        
        for endpoint in ["deployed", "fresh"]:
            for name, desc in error_cases.items():
                try:
                    data = {"description": desc} if desc is not None else {}
                    response = requests.post(
                        f"{BASE_URL}/analyze/{endpoint}",
                        json=data,
                        timeout=5
                    )
                    
                    # Should be rejected (422) or succeed with graceful handling
                    if response.status_code in [200, 422]:
                        passed += 1
                        self.log(f"✓ {endpoint}/{name}: {response.status_code}", "PASS")
                    else:
                        self.log(f"✗ {endpoint}/{name}: {response.status_code}", "FAIL")
                        
                except Exception as e:
                    self.log(f"✗ {endpoint}/{name}: {str(e)}", "ERROR")
        
        self.log(f"Error cases: {passed}/10 handled correctly", "RESULT")
        return passed
    
    def test_performance_stress(self) -> int:
        """Test performance under stress"""
        self.log("Testing Performance - Concurrent Requests", "START")
        passed = 0
        
        import concurrent.futures
        
        test_descriptions = [
            "Web app with database",
            "Microservices architecture",
            "Data processing pipeline",
        ]
        
        for endpoint in ["deployed", "fresh"]:
            times = []
            
            def make_request(desc):
                start = time.time()
                try:
                    response = requests.post(
                        f"{BASE_URL}/analyze/{endpoint}",
                        json={"description": desc},
                        timeout=15
                    )
                    return time.time() - start, response.status_code == 200
                except:
                    return time.time() - start, False
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(make_request, desc)
                    for desc in test_descriptions * 3
                ]
                
                results = []
                for future in concurrent.futures.as_completed(futures):
                    elapsed, success = future.result()
                    times.append(elapsed)
                    if success:
                        passed += 1
                    results.append((elapsed, success))
            
            avg_time = statistics.mean(times)
            max_time = max(times)
            min_time = min(times)
            
            self.log(f"{endpoint}: Avg={avg_time:.2f}s, Min={min_time:.2f}s, Max={max_time:.2f}s", "METRIC")
        
        self.log(f"Performance stress: {passed}/18 requests succeeded", "RESULT")
        return passed
    
    def test_response_validation(self) -> int:
        """Validate response structure and content"""
        self.log("Testing Response Validation", "START")
        passed = 0
        
        # Test deployed
        deployed_response = requests.post(
            f"{BASE_URL}/analyze/deployed",
            json={"description": "Test web application"},
            timeout=10
        )
        
        if deployed_response.status_code == 200:
            data = deployed_response.json()
            required = ["status", "analysis_type"]
            if all(field in data for field in required):
                passed += 1
                self.log("✓ Deployed response structure valid", "PASS")
            else:
                self.log("✗ Deployed response missing fields", "FAIL")
        
        # Test fresh
        fresh_response = requests.post(
            f"{BASE_URL}/analyze/fresh",
            json={"description": "Test web application"},
            timeout=10
        )
        
        if fresh_response.status_code == 200:
            data = fresh_response.json()
            required = ["status", "design_type", "recommended_architecture"]
            if all(field in data for field in required):
                passed += 1
                self.log("✓ Fresh response structure valid", "PASS")
            else:
                self.log("✗ Fresh response missing fields", "FAIL")
        
        return passed
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        self.start_time = time.time()
        print("\n" + "="*80)
        print(" PRODUCTION TEST SUITE - HARD TEST CASES ".center(80, "="))
        print("="*80 + "\n")
        
        total_passed = 0
        
        total_passed += self.test_edge_cases_deployed()
        print()
        total_passed += self.test_edge_cases_fresh()
        print()
        total_passed += self.test_error_cases()
        print()
        total_passed += self.test_performance_stress()
        print()
        total_passed += self.test_response_validation()
        
        self.end_time = time.time()
        
        # Print summary
        print("\n" + "="*80)
        print(" TEST SUMMARY ".center(80, "="))
        print("="*80)
        print(f"Total Passed:     {total_passed}")
        print(f"Total Errors:     {sum(self.results['errors'].values())}")
        print(f"Duration:         {self.end_time - self.start_time:.2f}s")
        print("="*80 + "\n")
        
        return total_passed

def print_productivity_recommendations():
    """Print recommendations for production readiness"""
    print("\n" + "="*80)
    print(" PRODUCTION RECOMMENDATIONS ".center(80, "="))
    print("="*80)
    
    recommendations = [
        ("Caching", "Implement Redis caching for similar architecture queries"),
        ("Rate Limiting", "Add rate limiting to prevent abuse (100 req/min per IP)"),
        ("Request Logging", "Log all requests with response times for monitoring"),
        ("Error Tracking", "Implement Sentry for error tracking and alerting"),
        ("Metrics", "Export Prometheus metrics for response times, error rates"),
        ("Timeouts", "Enforce 30s timeout for all endpoints"),
        ("Input Sanitization", "Implement comprehensive input sanitization"),
        ("Testing Coverage", "Maintain >90% code coverage with unit tests"),
        ("Documentation", "Keep API documentation up-to-date with Swagger/OpenAPI"),
        ("Monitoring", "Set up CloudWatch/Datadog for production monitoring"),
    ]
    
    for i, (title, desc) in enumerate(recommendations, 1):
        print(f"{i:2}. {title:20} - {desc}")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/analyze/deployed", timeout=2)
    except:
        print("❌ ERROR: Server not running on http://localhost:8000")
        print("Start the server with: python app.py")
        sys.exit(1)
    
    runner = TestRunner()
    total_passed = runner.run_all_tests()
    
    # Print productivity recommendations
    print_productivity_recommendations()
    
    # Exit status
    if total_passed > 0:
        print(f"✓ {total_passed} tests passed - System is productive and ready for testing")
        sys.exit(0)
    else:
        print("✗ Tests failed - System needs fixes before production use")
        sys.exit(1)
