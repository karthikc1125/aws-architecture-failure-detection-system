"""
Quick test for new deployed/fresh analysis endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test data
deployed_architecture = "I have 3 EC2 instances behind ALB with RDS master-slave, API Gateway with Lambda for triggers, S3 for static files, but experiencing timeouts during peak hours and no multi-AZ setup"

fresh_requirements = "Building a real-time collaboration platform with WebSockets, need to support 100K concurrent users, store user data and documents, requires GDPR compliance, expect 5M requests/day"

print("=" * 60)
print("Testing New Analysis Endpoints")
print("=" * 60)

# Test 1: Deployed System Analysis
print("\n1️⃣ Testing /api/analyze/deployed endpoint...")
try:
    response = requests.post(f"{BASE_URL}/api/analyze/deployed", json={
        "description": deployed_architecture,
        "provider": "openrouter",
        "model_id": "google/gemini-2.0-flash-exp:free"
    })
    
    if response.status_code == 200:
        result = response.json()
        print("✅ SUCCESS - Deployed System Analysis")
        print(f"   Analysis Type: {result.get('analysis_type')}")
        print(f"   Health Score: {result.get('health_score')}/100")
        print(f"   Issues Found: {result.get('total_issues')}")
        print(f"   Risks: {result.get('total_risks')}")
        print(f"   Optimization Opportunities: {result.get('total_optimizations')}")
    else:
        print(f"❌ FAILED - Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

# Test 2: Fresh Deployment Design
print("\n2️⃣ Testing /api/analyze/fresh endpoint...")
try:
    response = requests.post(f"{BASE_URL}/api/analyze/fresh", json={
        "description": fresh_requirements,
        "provider": "openrouter",
        "model_id": "google/gemini-2.0-flash-exp:free"
    })
    
    if response.status_code == 200:
        result = response.json()
        print("✅ SUCCESS - Fresh Deployment Design")
        print(f"   Analysis Type: {result.get('analysis_type')}")
        print(f"   Project Type: {result.get('project_type')}")
        print(f"   Estimated Scale: {result.get('estimated_scale')}")
        print(f"   Components: {len(result.get('recommended_architecture', []))} recommended")
        print(f"   Estimated Cost: {result.get('estimated_cost')}")
        print(f"   Readiness Score: {result.get('readiness_score')}/10")
    else:
        print(f"❌ FAILED - Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
