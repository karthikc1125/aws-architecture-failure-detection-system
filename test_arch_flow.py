from agents.failure_prediction_agent import FailurePredictionAgent
from agents.architecture_agent import ArchitectureAgent
import sys

# Simulation Script for Full Flow
def test_architecture_flow():
    print("Initializing Agents...")
    failure_agent = FailurePredictionAgent()
    architect_agent = ArchitectureAgent()
    
    # Test Input: The "Viral Marketing" scenario again
    input_scenario = """
    Viral marketing campaign. 
    Users upload images to S3.
    Lambda triggers immediately to resize.
    Writes to single DynamoDB partition.
    Synchronous processing.
    """
    
    # Step 1: Detect Failures
    print("\n--- 1. Detect Failures ---")
    failures = failure_agent.run(input_scenario)
    for f in failures:
        print(f"🔴 Detected: {f.name}")

    # Step 2: Propose Architecture
    print("\n--- 2. Design Architecture ---")
    architecture = architect_agent.run(failures)
    
    print("\n--- 🏗️ FINAL DESIGN OUTPUT ---")
    print(architecture.description)
    print("\nIncludes Components:")
    for c in architecture.components:
        print(f"  - 📦 {c.name} ({c.type})")

if __name__ == "__main__":
    test_architecture_flow()
