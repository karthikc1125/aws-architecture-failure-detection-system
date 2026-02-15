import unittest
import sys
import os
from agents.failure_prediction_agent import FailurePredictionAgent

class TestGraphAnalysis(unittest.TestCase):
    def setUp(self):
        self.agent = FailurePredictionAgent()

    def test_cyclic_dependency(self):
        """Test detection of a 3-node cycle in the architecture."""
        scenario_description = """
        We have an OrderService Lambda that sends messages to an SQS OrderQueue.
        The OrderQueue triggers an OrderProcessor Lambda.
        The OrderProcessor Lambda updates the status by calling the OrderService Lambda again.
        """
        
        failures = self.agent.run(scenario_description)
        
        # Check if Cycle Detected
        cycle_found = any(f.name == "Cyclic Dependency" for f in failures)
        self.assertTrue(cycle_found, "The agent should detect a cyclic dependency.")
        
        # Verify details
        for f in failures:
            if f.name == "Cyclic Dependency":
                self.assertIn("sqs_order", f.description)
                self.assertEqual(f.likelihood, 95)

    def test_spof_detection(self):
        """Test detection of a Single Point of Failure (SPOF)."""
        scenario = """
        ServiceLambdaA writes to MainRDS.
        ServiceLambdaB reads from MainRDS.
        ServiceLambdaC queries MainRDS.
        MainRDS is a single RDS instance in us-east-1a.
        """
        failures = self.agent.run(scenario)
        
        spof_found = any(f.name == "Single Point of Failure" for f in failures)
        self.assertTrue(spof_found, "The agent should detect a single point of failure.")

    def test_bottleneck_detection(self):
        """Test detection of a resource bottleneck."""
        scenario = """
        UserLambda calls InventoryLambda.
        OrderLambda calls InventoryLambda.
        ShippingLambda calls InventoryLambda.
        PaymentLambda queries InventoryLambda.
        Note: InventoryLambda is a single function with default concurrency.
        """
        failures = self.agent.run(scenario)
        
        bottleneck_found = any(f.name == "Resource Bottleneck" for f in failures)
        self.assertTrue(bottleneck_found, "The agent should detect a resource bottleneck.")
        
        # Verify it identifies the correct service
        for f in failures:
            if f.name == "Resource Bottleneck":
                self.assertIn("inventory", f.description)

if __name__ == '__main__':
    unittest.main()
