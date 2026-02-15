import yaml
import os
import json
from typing import List
from agents.base_agent import BaseAgent
from rag.retriever import Retriever
from schemas.failure_schema import FailureMode
from agents.text_to_graph import TextToGraphParser
from agents.iac_parser import TerraformParser

class FailurePredictionAgent(BaseAgent):
    def __init__(self):
        super().__init__("FailurePredictionAgent", "agents/prompts/failure_agent.txt")
        self.retriever = Retriever()
        self.patterns = self._load_patterns()
        self.parser = TextToGraphParser()
        self.iac_parser = TerraformParser()

    def _load_patterns(self):
        """Loads deterministic failure patterns from YAML files."""
        patterns = []
        pattern_dir = "patterns"
        if os.path.exists(pattern_dir):
            for f in os.listdir(pattern_dir):
                if f.endswith(".yaml") or f.endswith(".yml"):
                    with open(os.path.join(pattern_dir, f), 'r') as file:
                        patterns.append(yaml.safe_load(file))
        return patterns

    def run(self, project_description: str) -> List[FailureMode]:
        print(f"[{self.name}] Analyzing project: {project_description[:50]}...")
        detected_failures = []
        lower_desc = project_description.lower()
        
        # Check if input is a file path (Terraform mode)
        if os.path.exists(project_description) and (project_description.endswith(".tf") or os.path.isdir(project_description)):
            print(f"[{self.name}] Detected Infrastructure as Code input.")
            if os.path.isdir(project_description):
                graph = self.iac_parser.parse_directory(project_description)
            else:
                graph = self.iac_parser.parse_file(project_description)
                
            graph_findings = self.iac_parser.analyze_graph(graph)
        else:
            # 1. Retrieve Context (History)
            context = self.retriever.retrieve(project_description)
            retrieved_text = context.get("formatted_context", "")
            
            # 2. Graph Analysis (New Logic)
            print(f"[{self.name}] Building Architecture Graph using NLP...")
            graph = self.parser.parse(lower_desc)
            graph_findings = self.parser.analyze_graph(graph)
        
        for finding in graph_findings:
            # Map graph findings to FailureMode objects
            if "Cycle" in finding:
                detected_failures.append(FailureMode(
                    name="Cyclic Dependency",
                    failure_class="Architectural Flaw",
                    description=f"Infinite loop detected in service structure: {finding}",
                    mitigation="Decouple services using SQS/SNS or Step Functions.",
                    likelihood=95
                ))
            elif "SPOF" in finding:
                detected_failures.append(FailureMode(
                    name="Single Point of Failure",
                    failure_class="Availability Risk",
                    description=finding,
                    mitigation="Implement Multi-AZ redundancy or Auto Scaling.",
                    likelihood=85
                ))
            elif "Bottleneck" in finding:
                detected_failures.append(FailureMode(
                    name="Resource Bottleneck",
                    failure_class="Performance Degradation",
                    description=finding,
                    mitigation="Introduce caching (ElastiCache) or sharding.",
                    likelihood=80
                ))
            elif "Config Issue" in finding:
                detected_failures.append(FailureMode(
                    name="Configuration Issue",
                    failure_class="Operational Risk",
                    description=finding,
                    mitigation="Review and update resource configuration to meet best practices.",
                    likelihood=70
                ))
            elif "Security Issue" in finding:
                detected_failures.append(FailureMode(
                    name="Security Misconfiguration",
                    failure_class="Security Risk",
                    description=finding,
                    mitigation="Enable encryption and security controls.",
                    likelihood=90
                ))
            elif "Reliability Issue" in finding:
                detected_failures.append(FailureMode(
                    name="Reliability Risk",
                    failure_class="Data Loss Risk",
                    description=finding,
                    mitigation="Increase backup retention and implement disaster recovery.",
                    likelihood=75
                ))
            elif "Availability Issue" in finding:
                detected_failures.append(FailureMode(
                    name="Availability Risk",
                    failure_class="High Availability",
                    description=finding,
                    mitigation="Enable Multi-AZ deployment for high availability.",
                    likelihood=80
                ))
            elif "Data Protection Issue" in finding:
                detected_failures.append(FailureMode(
                    name="Data Protection Risk",
                    failure_class="Data Loss Risk",
                    description=finding,
                    mitigation="Enable versioning and point-in-time recovery.",
                    likelihood=75
                ))


        # 3. Pattern Matching (Deterministic Rules)
        for pattern in self.patterns:
            required_conditions = pattern.get("conditions", [])
            conditions_met = 0
            
            # Refined Simulation Logic:
            # We treat the text description as a bag of concepts.
            # In a real system, the LLM would do semantic matching.
            # Here, we require a stronger match ratio or specific keywords.
            
            for condition in required_conditions:
                # Basic normalization
                condition_clean = condition.replace("_", " ")
                
                # Check if the *concept* of the condition exists in text
                # This is a naive simulation. 
                # e.g. "synchronous calls" -> matches "synchronous"
                keywords = condition_clean.split()
                if any(k in lower_desc for k in keywords):
                    conditions_met += 1
            
            # Threshold: detect if at least 50% of conditions are hinted at
            match_ratio = conditions_met / len(required_conditions) if required_conditions else 0
            
            if len(required_conditions) > 0 and match_ratio >= 0.5:
                # Calculate Likelihood Score (0-100%)
                # Base score from match ratio + slight variability based on pattern complexity
                likelihood_score = int(match_ratio * 100)
                
                # Boost likelihood for critical patterns (e.g., race conditions, SPOFs)
                if any(x in pattern.get("pattern", "") for x in ["race", "spof", "collision", "exhaustion"]):
                    likelihood_score = min(likelihood_score + 10, 99)

                detected_failures.append(FailureMode(
                    name=pattern.get("pattern", "General Failure"),
                    failure_class=pattern.get("failure_class", "Unknown"),
                    description=f"Potential for {pattern.get('pattern')} detected. Conditions identified in text.",
                    mitigation=", ".join(pattern.get("mitigations", [])),
                    likelihood=likelihood_score
                ))

        # 3. LLM "Thinking" (Simulation)
        # If we had a real API key, we'd send the prompt here.
        # prompt = self.prompt_template.replace("{{CONTEXT}}", retrieved_text)
        
        return detected_failures
