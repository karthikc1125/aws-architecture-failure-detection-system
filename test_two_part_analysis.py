#!/usr/bin/env python3
"""
Test the two-part analysis endpoints:
1. /api/analyze/deployed - for existing deployments
2. /api/analyze/fresh - for new deployments
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_deployed_analysis():
    """Test deployed system analysis endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Analyze Deployed System")
    print("="*60)
    
    payload = {
        "description": "We have 3 EC2 instances behind ALB with RDS master-slave, API Gateway with Lambda for triggers, S3 for static files, but experiencing timeouts during peak hours and no multi-AZ setup",
        "provider": "openrouter",
        "model_id": "google/gemini-2.0-flash-exp:free"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/analyze/deployed",
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_fresh_deployment():
    """Test fresh deployment design endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Design Fresh Deployment")
    print("="*60)
    
    payload = {
        "description": "Building a real-time collaboration platform with WebSockets, need to support 1M concurrent users, store user data and documents, requires GDPR compliance, expect 50M requests/day",
        "provider": "openrouter",
        "model_id": "google/gemini-2.0-flash-exp:free"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/analyze/fresh",
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_invalid_input():
    """Test with invalid input"""
    print("\n" + "="*60)
    print("TEST 3: Invalid Input Handling")
    print("="*60)
    
    payload = {
        "description": "short",  # Too short
        "provider": "openrouter",
        "model_id": "google/gemini-2.0-flash-exp:free"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/analyze/deployed",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            print("✅ Correctly rejected invalid input")
            return True
        else:
            print(f"❌ Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Two-Part Analysis Endpoints")
    print("Base URL:", API_BASE)
    
    results = {
        "test_deployed": test_deployed_analysis(),
        "test_fresh": test_fresh_deployment(),
        "test_invalid": test_invalid_input()
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    return all_passed

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
