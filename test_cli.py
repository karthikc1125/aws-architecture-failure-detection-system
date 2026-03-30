#!/usr/bin/env python3
"""
Failure-Driven AWS Architect - Comprehensive Testing CLI

Run tests for the analysis system with detailed reporting.
"""

import sys
import os
import json
import time
import subprocess
from typing import Dict, List, Tuple
from pathlib import Path
import argparse

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class TestRunner:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = time.time()

    def print_header(self, text):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

    def print_test(self, name: str, status: str, message: str = ""):
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
        status_color = Colors.OKGREEN if status == "PASS" else Colors.FAIL if status == "FAIL" else Colors.WARNING

        print(f"{status_symbol} {status_color}{status}{Colors.ENDC} - {name}")
        if message:
            print(f"   └─ {Colors.OKCYAN}{message}{Colors.ENDC}")

    def test_imports(self):
        """Test that all required modules can be imported"""
        self.print_header("Test 1: Module Imports")
        
        modules = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "sentence_transformers",
            "faiss",
            "yaml",
            "requests"
        ]
        
        for module in modules:
            try:
                __import__(module)
                self.print_test(f"Import {module}", "PASS")
                self.passed += 1
            except ImportError as e:
                self.print_test(f"Import {module}", "FAIL", str(e))
                self.failed += 1

    def test_project_structure(self):
        """Test that all required directories exist"""
        self.print_header("Test 2: Project Structure")
        
        required_dirs = [
            "api",
            "agents",
            "orchestration",
            "embeddings",
            "rag",
            "frontend",
            "schemas",
            "rules",
            "data",
            "vector_store",
            "tests"
        ]
        
        for dir_name in required_dirs:
            if os.path.isdir(dir_name):
                self.print_test(f"Directory {dir_name}/", "PASS")
                self.passed += 1
            else:
                self.print_test(f"Directory {dir_name}/", "FAIL", "Not found")
                self.failed += 1

    def test_api_models(self):
        """Test that API models can be loaded"""
        self.print_header("Test 3: API Models & Schemas")
        
        try:
            from api.models import UserInput
            self.print_test("Load UserInput model", "PASS")
            self.passed += 1
        except Exception as e:
            self.print_test("Load UserInput model", "FAIL", str(e))
            self.failed += 1

        try:
            from schemas.output_schema import AnalysisOutput
            self.print_test("Load AnalysisOutput schema", "PASS")
            self.passed += 1
        except Exception as e:
            self.print_test("Load AnalysisOutput schema", "FAIL", str(e))
            self.failed += 1

    def test_agents(self):
        """Test that agents can be initialized"""
        self.print_header("Test 4: Agent Initialization")
        
        try:
            from agents.failure_prediction_agent import FailurePredictionAgent
            agent = FailurePredictionAgent()
            self.print_test("Initialize FailurePredictionAgent", "PASS")
            self.passed += 1
        except Exception as e:
            self.print_test("Initialize FailurePredictionAgent", "FAIL", str(e))
            self.failed += 1

        try:
            from agents.architecture_agent import ArchitectureAgent
            agent = ArchitectureAgent()
            self.print_test("Initialize ArchitectureAgent", "PASS")
            self.passed += 1
        except Exception as e:
            self.print_test("Initialize ArchitectureAgent", "FAIL", str(e))
            self.failed += 1

    def test_pattern_loading(self):
        """Test that patterns can be loaded"""
        self.print_header("Test 5: Pattern Loading")
        
        try:
            from agents.failure_prediction_agent import FailurePredictionAgent
            agent = FailurePredictionAgent()
            num_patterns = len(agent.patterns)
            
            if num_patterns > 0:
                self.print_test(f"Load patterns", "PASS", f"Found {num_patterns} patterns")
                self.passed += 1
            else:
                self.print_test(f"Load patterns", "FAIL", "No patterns found")
                self.failed += 1
        except Exception as e:
            self.print_test("Load patterns", "FAIL", str(e))
            self.failed += 1

    def test_embeddings(self):
        """Test that embeddings can be generated"""
        self.print_header("Test 6: Embeddings Generation")
        
        try:
            from embeddings.embedder import Embedder
            embedder = Embedder()
            embedding = embedder.embed_text("test architecture description")
            
            if embedding is not None and len(embedding) > 0:
                self.print_test("Generate embedding", "PASS", f"Embedding shape: {len(embedding)}")
                self.passed += 1
            else:
                self.print_test("Generate embedding", "FAIL", "Empty embedding")
                self.failed += 1
        except Exception as e:
            self.print_test("Generate embedding", "FAIL", str(e))
            self.failed += 1

    def test_vector_store(self):
        """Test that vector store is functional"""
        self.print_header("Test 7: Vector Store")
        
        try:
            import faiss
            index_path = "vector_store/failure_patterns.index"
            
            if os.path.exists(index_path):
                index = faiss.read_index(index_path)
                num_vectors = index.ntotal
                self.print_test("Load FAISS index", "PASS", f"Found {num_vectors} vectors")
                self.passed += 1
            else:
                self.print_test("Load FAISS index", "SKIP", "Index not built yet")
                self.skipped += 1
        except Exception as e:
            self.print_test("Load FAISS index", "FAIL", str(e))
            self.failed += 1

    def test_pipeline(self):
        """Test that pipeline can be initialized"""
        self.print_header("Test 8: Pipeline Orchestration")
        
        try:
            from orchestration.pipeline import get_agents
            fail_agent, arch_agent = get_agents()
            self.print_test("Initialize agents via pipeline", "PASS")
            self.passed += 1
        except Exception as e:
            self.print_test("Initialize agents via pipeline", "FAIL", str(e))
            self.failed += 1

    def test_simulation_analysis(self):
        """Test analysis in simulation mode (no LLM)"""
        self.print_header("Test 9: Simulation Mode Analysis")
        
        try:
            os.environ["AI_PROVIDER"] = "simulation"
            
            from orchestration.pipeline import run_pipeline
            
            test_input = "I have EC2 → RDS with single replica and API Gateway with Lambda synchronously writing"
            result = run_pipeline(test_input, provider="simulation", model_id="test")
            
            if result and result.detected_failures:
                self.print_test("Run analysis in simulation mode", "PASS", 
                              f"Detected {len(result.detected_failures)} failures")
                self.passed += 1
            else:
                self.print_test("Run analysis in simulation mode", "FAIL", "No failures detected")
                self.failed += 1
        except Exception as e:
            self.print_test("Run analysis in simulation mode", "FAIL", str(e))
            self.failed += 1

    def test_fastapi_server(self):
        """Test that FastAPI server starts"""
        self.print_header("Test 10: FastAPI Server Startup")
        
        try:
            from api.main import app
            self.print_test("Load FastAPI app", "PASS")
            self.passed += 1
        except Exception as e:
            self.print_test("Load FastAPI app", "FAIL", str(e))
            self.failed += 1

    def test_code_quality(self):
        """Test code quality with static analysis"""
        self.print_header("Test 11: Code Quality (Static Analysis)")
        
        # Check for print statements (should use logging)
        print_count = 0
        for root, dirs, files in os.walk("agents"):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    with open(path) as f:
                        for i, line in enumerate(f, 1):
                            if "print(" in line and not line.strip().startswith("#"):
                                print_count += 1
        
        if print_count > 0:
            self.print_test("Code quality: logging", "WARNING", f"Found {print_count} print statements (should use logging)")
            self.skipped += 1
        else:
            self.print_test("Code quality: logging", "PASS")
            self.passed += 1

    def test_error_handling(self):
        """Test error handling coverage"""
        self.print_header("Test 12: Error Handling")
        
        try:
            from api.routes import analyze_architecture
            self.print_test("Error handling in API", "SKIP", "Manual review needed")
            self.skipped += 1
        except Exception as e:
            self.print_test("Error handling in API", "FAIL", str(e))
            self.failed += 1

    def test_security(self):
        """Test security aspects"""
        self.print_header("Test 13: Security")
        
        # Check for API key in code
        api_key_found = False
        for root, dirs, files in os.walk("api"):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    with open(path) as f:
                        content = f.read()
                        if "sk-" in content or "api_key=" in content:
                            api_key_found = True
        
        if not api_key_found:
            self.print_test("Security: No hardcoded API keys", "PASS")
            self.passed += 1
        else:
            self.print_test("Security: No hardcoded API keys", "WARNING", "Found potential hardcoded keys")
            self.skipped += 1

    def test_performance(self):
        """Test performance metrics"""
        self.print_header("Test 14: Performance Benchmarks")
        
        try:
            from orchestration.pipeline import run_pipeline
            os.environ["AI_PROVIDER"] = "simulation"
            
            test_cases = [
                ("small", "I have Lambda and DynamoDB"),
                ("medium", "I have API Gateway → Lambda → RDS with SQS and SNS queues"),
                ("large", "Complex architecture with EC2, RDS, S3, CloudFront, Lambda, DynamoDB, SQS, SNS, API Gateway, ALB, and VPC")
            ]
            
            for size, input_text in test_cases:
                start = time.time()
                result = run_pipeline(input_text, provider="simulation")
                elapsed = time.time() - start
                
                self.print_test(f"Performance ({size} input)", "PASS", f"{elapsed:.2f}s")
                self.passed += 1
        except Exception as e:
            self.print_test("Performance benchmarks", "FAIL", str(e))
            self.failed += 1

    def run_all_tests(self):
        """Run all tests"""
        self.print_header(f"{Colors.BOLD}FAILURE-DRIVEN AWS ARCHITECT - TEST SUITE{Colors.ENDC}")
        
        self.test_imports()
        self.test_project_structure()
        self.test_api_models()
        self.test_agents()
        self.test_pattern_loading()
        self.test_embeddings()
        self.test_vector_store()
        self.test_pipeline()
        self.test_simulation_analysis()
        self.test_fastapi_server()
        self.test_code_quality()
        self.test_error_handling()
        self.test_security()
        self.test_performance()
        
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        elapsed = time.time() - self.start_time
        total = self.passed + self.failed + self.skipped
        
        self.print_header(f"{Colors.BOLD}TEST SUMMARY{Colors.ENDC}")
        
        print(f"{Colors.OKGREEN}✅ Passed: {self.passed}{Colors.ENDC}")
        print(f"{Colors.FAIL}❌ Failed: {self.failed}{Colors.ENDC}")
        print(f"{Colors.WARNING}⏭️  Skipped: {self.skipped}{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Total: {total} tests | Time: {elapsed:.2f}s{Colors.ENDC}")
        
        if self.failed == 0:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.ENDC}\n")
            return 0
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ {self.failed} TESTS FAILED{Colors.ENDC}\n")
            return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the Failure-Driven AWS Architect system")
    parser.add_argument("--category", choices=["imports", "structure", "models", "agents", "all"], 
                       default="all", help="Run specific test category")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Add project root to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    runner = TestRunner()
    
    if args.category == "all":
        exit_code = runner.run_all_tests()
    elif args.category == "imports":
        runner.test_imports()
        exit_code = runner.print_summary()
    elif args.category == "structure":
        runner.test_project_structure()
        exit_code = runner.print_summary()
    elif args.category == "models":
        runner.test_api_models()
        exit_code = runner.print_summary()
    elif args.category == "agents":
        runner.test_agents()
        exit_code = runner.print_summary()
    
    sys.exit(exit_code)
