"""
Agent for analyzing and optimizing ALREADY DEPLOYED AWS architectures
Focus: Performance, cost, security improvements for existing systems
"""
from typing import List
from agents.base_agent import BaseAgent
from schemas.failure_schema import FailureMode
from schemas.architecture_schema import Architecture, ArchitectureComponent

class DeployedArchitectureAgent(BaseAgent):
    """Analyzes existing, deployed AWS architectures for optimization"""
    
    def __init__(self):
        super().__init__("DeployedArchitectureAgent", "agents/prompts/deployed_agent.txt")
        self.focus_areas = [
            "Cost optimization",
            "Performance bottlenecks", 
            "Security vulnerabilities",
            "Operational efficiency",
            "Redundancy gaps",
            "Compliance issues"
        ]

    def run(self, description: str, provider: str = "openrouter", model_id: str = None) -> dict:
        """
        Analyze existing deployed architecture
        Returns: {issues, optimizations, cost_savings, security_improvements, implementation_effort}
        """
        print(f"[{self.name}] 🏗️ Analyzing DEPLOYED architecture...")
        print(f"[{self.name}] Focus areas: {', '.join(self.focus_areas)}")
        
        self.provider = provider
        self.model_id = model_id
        
        # Build analysis prompt
        analysis_prompt = f"""
You are an AWS architecture optimization expert analyzing a DEPLOYED system.

Current Architecture:
{description}

Analyze for:
1. **Cost Optimization** - Where can we save money?
2. **Performance** - What's slow or inefficient?
3. **Security** - What vulnerabilities exist?
4. **Redundancy** - What needs backup/failover?
5. **Operations** - What's hard to manage?
6. **Compliance** - What's not compliant?

For each issue, provide:
- Severity (Critical/High/Medium/Low)
- Estimated savings/impact
- Implementation effort (1-5 hours)
- Quick wins vs long-term

Format as structured JSON with issues array.
"""
        
        # Call LLM
        llm_response = self._call_llm(
            system_prompt=self.prompt_template,
            user_input=analysis_prompt
        )
        
        if not llm_response:
            # Fallback analysis
            return self._fallback_deployed_analysis(description)
        
        return {
            "status": "analyzed",
            "analysis_type": "deployed_optimization",
            "recommendations": llm_response,
            "focus_areas": self.focus_areas
        }
    
    def _fallback_deployed_analysis(self, description: str) -> dict:
        """Fallback deterministic analysis for deployed architecture"""
        lower_desc = description.lower()
        issues = []
        optimizations = []
        
        # Check for common issues in deployed systems
        if "single" in lower_desc and "rds" in lower_desc:
            issues.append({
                "issue": "Single RDS Instance - No Multi-AZ",
                "severity": "High",
                "cost_impact": "Low cost but high risk",
                "optimization": "Enable Multi-AZ for $100-200/month more, massive reliability gain"
            })
        
        if "ec2" in lower_desc and "no cache" in lower_desc.lower():
            issues.append({
                "issue": "No caching layer detected",
                "severity": "Medium",
                "cost_impact": "Higher compute costs",
                "optimization": "Add ElastiCache Redis - $50-200/month, 10x faster responses"
            })
        
        if "manually" in lower_desc or "manual" in lower_desc:
            issues.append({
                "issue": "Manual deployment/operations",
                "severity": "High",
                "cost_impact": "High operational overhead",
                "optimization": "Implement CI/CD pipeline - Reduce ops time by 80%"
            })
        
        if "no monitoring" in lower_desc or "no logs" in lower_desc:
            issues.append({
                "issue": "Missing observability",
                "severity": "Critical",
                "cost_impact": "Risk of undetected issues",
                "optimization": "Add CloudWatch + X-Ray monitoring"
            })
        
        if "reserved capacity" not in lower_desc:
            optimizations.append({
                "opportunity": "Reserved Instances",
                "savings": "30-40% on compute costs",
                "effort": "1 hour",
                "monthly_savings": "$500-2000 depending on scale"
            })
        
        if "spot instances" not in lower_desc and "ec2" in lower_desc:
            optimizations.append({
                "opportunity": "Spot Instances for non-critical workloads",
                "savings": "70-90% on compute",
                "effort": "2-3 hours",
                "monthly_savings": "$1000-5000 depending on workload"
            })
        
        return {
            "status": "optimized",
            "analysis_type": "deployed_optimization",
            "issues": issues,
            "quick_wins": optimizations,
            "total_potential_savings": "20-40% of infrastructure costs",
            "implementation_effort": "1-2 weeks for full optimization"
        }
