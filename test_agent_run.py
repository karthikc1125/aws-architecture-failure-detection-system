from agents.failure_prediction_agent import FailurePredictionAgent
import json
import sys

# Simulation Script for Failure Agent
def test_agent():
    print("Initializing Failure Prediction Agent...")
    agent = FailurePredictionAgent()
    
    # Test Input: A scenario ripe for failure
    input_scenario = """
    We are building a viral marketing campaign. 
    Users upload images to an S3 bucket.
    A Lambda function triggers immediately on upload to resize the image.
    The Lambda writes metadata to a single DynamoDB partition.
    Everything is synchronous.
    """
    
    print("\n--- Running Analysis ---")
    failures = agent.run(input_scenario)
    
    print("\n--- 🛑 DETECTED FAILURES ---")
    for f in failures:
        print(f"🔴 {f.name} ({f.failure_class})")
        print(f"   Description: {f.description}")
        print(f"   Mitigation: {f.mitigation}")
        print("-" * 30)

if __name__ == "__main__":
    test_agent()
