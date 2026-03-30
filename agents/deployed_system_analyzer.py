"""
DeployedSystemAnalyzerAgent - Analyzes existing deployed systems
Focuses on: Issues, bottlenecks, optimization opportunities, failure risks
"""
from typing import List
from agents.base_agent import BaseAgent
from rag.retriever import Retriever
from schemas.failure_schema import FailureMode
from agents.text_to_graph import TextToGraphParser
from agents.iac_parser import TerraformParser
import yaml
import os


class DeployedSystemAnalyzerAgent(BaseAgent):
    """Analyzes already deployed AWS architectures for issues and improvements"""
    
    def __init__(self):
        super().__init__("DeployedSystemAnalyzerAgent", "agents/prompts/deployed_agent.txt")
        self.retriever = Retriever()
        self.patterns = self._load_patterns()
        self.parser = TextToGraphParser()
        self.iac_parser = TerraformParser()

    def _load_patterns(self):
        """Loads failure patterns from YAML files"""
        patterns = []
        pattern_dir = "patterns"
        if os.path.exists(pattern_dir):
            for f in os.listdir(pattern_dir):
                if f.endswith(".yaml") or f.endswith(".yml"):
                    with open(os.path.join(pattern_dir, f), 'r') as file:
                        patterns.append(yaml.safe_load(file))
        return patterns

    def run(self, system_description: str) -> dict:
        """
        Analyzes deployed system for:
        - Current issues and failures
        - Performance bottlenecks
        - Cost optimization opportunities
        - Security vulnerabilities
        - Operational risks
        """
        print(f"[{self.name}] Analyzing deployed system: {system_description[:60]}...")
        
        issues_found = []
        optimization_suggestions = []
        risk_assessment = []
        
        lower_desc = system_description.lower()
        
        # 1. Parse architecture
        graph = self.parser.parse(lower_desc)
        graph_findings = self.parser.analyze_graph(graph)
        
        # 2. Pattern matching for current issues
        for pattern in self.patterns:
            pattern_keywords = pattern.get('keywords', []) if pattern else []
            if any(keyword in lower_desc for keyword in pattern_keywords):
                issues_found.append({
                    'pattern': pattern.get('name', 'Unknown'),
                    'description': pattern.get('description', ''),
                    'severity': pattern.get('severity', 'medium'),
                    'likelihood': pattern.get('likelihood', 50)
                })
        
        # 3. Graph analysis for failures
        for finding in graph_findings:
            if "SPOF" in finding:
                risk_assessment.append({
                    'type': 'Single Point of Failure',
                    'description': finding,
                    'impact': 'High - System outage if component fails',
                    'urgency': 'Critical'
                })
            elif "Bottleneck" in finding:
                optimization_suggestions.append({
                    'opportunity': 'Performance Bottleneck',
                    'description': finding,
                    'estimated_improvement': '30-50% latency reduction',
                    'implementation': 'Add caching (ElastiCache) or sharding'
                })
            elif "Cycle" in finding:
                risk_assessment.append({
                    'type': 'Circular Dependency',
                    'description': finding,
                    'impact': 'Medium - Hard to scale and maintain',
                    'urgency': 'High'
                })
        
        # 4. Cost optimization analysis
        if 'single' in lower_desc or 'standalone' in lower_desc:
            optimization_suggestions.append({
                'opportunity': 'Single Instance Running',
                'description': 'You may be over-provisioned or under-utilizing reserved instances',
                'estimated_improvement': '40-60% cost reduction',
                'implementation': 'Use auto-scaling groups, reserved instances, or spot instances'
            })
        
        if 'no backup' in lower_desc or 'no replica' in lower_desc:
            risk_assessment.append({
                'type': 'No Disaster Recovery',
                'description': 'System has no backup or failover strategy',
                'impact': 'Critical - Data loss in outage',
                'urgency': 'Critical'
            })
        
        return {
            'analysis_type': 'deployed_system',
            'current_issues': issues_found,
            'optimization_opportunities': optimization_suggestions,
            'risk_assessment': risk_assessment,
            'total_issues': len(issues_found),
            'total_risks': len(risk_assessment),
            'total_optimizations': len(optimization_suggestions),
            'health_score': max(0, 100 - (len(issues_found) * 10 + len(risk_assessment) * 15))
        }
