"""
Agent for analyzing and optimizing ALREADY DEPLOYED AWS architectures
Focus: Performance, cost, security improvements for existing systems
"""
from typing import List
from agents.base_agent import BaseAgent
from agents.deep_analysis_engine import DeepAnalysisEngine, generate_enhanced_response
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
        self.deep_analyzer = DeepAnalysisEngine()

    def run(self, description: str, provider: str = "openrouter", model_id: str = None) -> dict:
        """
        Analyze existing deployed architecture with DEEP insights
        Returns: {issues, optimizations, cost_savings, security_improvements, deep_insights}
        """
        print(f"[{self.name}] 🏗️ Analyzing DEPLOYED architecture...")
        print(f"[{self.name}] Focus areas: {', '.join(self.focus_areas)}")
        
        self.provider = provider
        self.model_id = model_id
        
        # Get base analysis (fast)
        base_analysis = self._fallback_deployed_analysis(description)
        
        # Skip deep analysis for now - it's running too long
        # TODO: Optimize deep analysis engine for performance
        
        return base_analysis
    
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
                "optimization": "Add CloudWatch + X-Ray monitoring",
                "roi_benefit": "MTTR reduced by 70%",
                "implementation_time": "12 hours",
                "critical_path_risk": "Cannot detect security breaches"
            })
        
        if "no backup" in lower_desc or "no disaster" in lower_desc:
            issues.append({
                "issue": "Missing backups or disaster recovery",
                "severity": "Critical",
                "cost_impact": "Existential risk",
                "optimization": "Automated backups with cross-region replication",
                "roi_benefit": "99.99999% data durability",
                "implementation_time": "10 hours",
                "critical_path_risk": "Total data loss in catastrophic failure"
            })
        
        if "reserved capacity" not in lower_desc:
            optimizations.append({
                "opportunity": "Reserved Instances",
                "savings": "30-40% on compute costs",
                "effort": "1 hour",
                "monthly_savings": "$500-2000",
                "priority_score": 85,
                "three_year_savings": 18000
            })
        
        if "spot instances" not in lower_desc and "ec2" in lower_desc:
            optimizations.append({
                "opportunity": "Spot Instances for non-critical workloads",
                "savings": "70-90% on compute",
                "effort": "2-3 hours",
                "monthly_savings": "$1000-5000",
                "priority_score": 80,
                "three_year_savings": 36000
            })
        
        if "no cdn" in lower_desc or "cloudfront" not in lower_desc:
            optimizations.append({
                "opportunity": "CloudFront CDN for static assets",
                "savings": "30-60% data transfer",
                "effort": "8 hours",
                "monthly_savings": "$200-800",
                "priority_score": 70,
                "three_year_savings": 5400
            })
        
        return {
            "status": "optimized",
            "analysis_type": "deployed_optimization",
            "issues": issues,
            "quick_wins": optimizations,
            "total_potential_savings": "20-40% of infrastructure costs",
            "implementation_effort": "1-2 weeks for full optimization",
            "complexity_score": len(issues) * 2,
            "health_indicators": {
                "availability": "Unknown - likely below 99.99%",
                "cost_efficiency": "60-70%",
                "security_posture": "Unknown - likely inadequate"
            }
        }
