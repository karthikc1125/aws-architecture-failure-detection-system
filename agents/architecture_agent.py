from typing import List, Dict
from agents.base_agent import BaseAgent
from schemas.failure_schema import FailureMode
from schemas.architecture_schema import Architecture, ArchitectureComponent
from rules.pattern_to_service import suggest_services_for_mitigation

class ArchitectureAgent(BaseAgent):
    def __init__(self):
        super().__init__("ArchitectureAgent", "agents/prompts/architect_agent.txt")

    def run(self, failures: List[FailureMode]) -> Architecture:
        print(f"[{self.name}] Designing Architecture based on {len(failures)} failures...")
        
        proposed_components = []
        design_rationale = []

        # 1. Base Architecture (Implicit)
        # In a real agent, we'd parse the user's input to keep what's good.
        # Here, we focus on *adding* the mitigations.
        
        # 2. Apply Mitigations
        unique_components = set()

        for failure in failures:
            print(f"  👉 Mitigating {failure.name}...")
            if failure.mitigation:
                strategies = [m.strip() for m in failure.mitigation.split(',')]
                
                for strategy in strategies:
                    recommended_services = suggest_services_for_mitigation(strategy)
                    
                    if recommended_services:
                        # Pick the primary recommendation for simplicity in this deterministic logic
                        primary_service = recommended_services[0]
                        
                        if primary_service not in unique_components:
                            comp = ArchitectureComponent(
                                name=f"Resilient-{primary_service}", 
                                type=primary_service, 
                                connections=[] 
                            )
                            proposed_components.append(comp)
                            unique_components.add(primary_service)
                            
                        design_rationale.append(f"Added {primary_service} to address {failure.name} ({strategy}).")

        # 3. Construct Final Design
        description = "Proposed Resilient Architecture:\n" + "\n".join([f"- {r}" for r in design_rationale])
        
        return Architecture(
            components=proposed_components,
            description=description
        )
