"""
Agent for suggesting architecture for FRESH/NEW AWS deployments
Focus: Design best practices, scalability, resilience from day 1
"""
from typing import List, Dict
from agents.base_agent import BaseAgent
from agents.deep_analysis_engine import DeepAnalysisEngine
from schemas.architecture_schema import Architecture, ArchitectureComponent

class FreshDeploymentAgent(BaseAgent):
    """Designs optimal AWS architectures for new/greenfield projects"""
    
    def __init__(self):
        super().__init__("FreshDeploymentAgent", "agents/prompts/fresh_agent.txt")
        self.design_principles = [
            "Design for failure from day 1",
            "Multi-AZ availability",
            "Auto-scaling readiness",
            "Cost optimization built-in",
            "Security by default",
            "Observability from start"
        ]
        self.deep_analyzer = DeepAnalysisEngine()

    def run(self, description: str, provider: str = "openrouter", model_id: str = None) -> dict:
        """
        Design architecture for fresh deployment with DEEP insights
        Returns: {recommended_architecture, components, scalability_path, estimated_cost, timeline, risk_analysis}
        """
        print(f"[{self.name}] 🆕 Designing FRESH deployment architecture...")
        print(f"[{self.name}] Principles: {', '.join(self.design_principles)}")
        
        self.provider = provider
        self.model_id = model_id
        
        # Get base design
        base_design = self._fallback_fresh_design(description)
        # Add advanced insights
        enhanced_design = self._enhance_design_with_deep_insights(description, base_design)
        
        return enhanced_design
    
    def _enhance_design_with_deep_insights(self, description: str, base_design: dict) -> dict:
        """Enhance design with advanced risk analysis and insights"""
        # Add complexity assessment
        complexity_keywords = {
            "multi_region": ["multi-region", "global", "edge"],
            "real_time": ["real-time", "streaming", "live", "websocket"],
            "high_scale": ["million users", "million transactions", "petabyte"],
            "compliance": ["hipaa", "pci", "gdpr", "sox"]
        }
        
        complexity_score = 0
        special_requirements = []
        for req, keywords in complexity_keywords.items():
            if any(kw in description.lower() for kw in keywords):
                complexity_score += 1
                special_requirements.append(req)
        
        # Risk mitigation strategies
        risk_mitigations = {
            "multi_region": {
                "risk": "Regional outages",
                "mitigation": "Deploy to multiple regions with Route53 failover",
                "cost_delta": "+40-60% but 99.99% availability"
            },
            "real_time": {
                "risk": "Message loss and latency",
                "mitigation": "Use SQS/SNS/Kinesis with DLQ and monitoring",
                "cost_delta": "+20-30%"
            },
            "high_scale": {
                "risk": "Database bottlenecks",
                "mitigation": "Implement read replicas, caching layer, and sharding",
                "cost_delta": "+50-100%"
            },
            "compliance": {
                "risk": "Regulatory non-compliance",
                "mitigation": "Encryption, audit logging, data residency controls",
                "cost_delta": "+15-25%"
            }
        }
        
        # Generate risk analysis
        risk_analysis = []
        for req in special_requirements:
            if req in risk_mitigations:
                risk_analysis.append(risk_mitigations[req])
        
        # Add to base design
        enhanced = {
            **base_design,
            "design_complexity": complexity_score,
            "special_requirements": special_requirements,
            "risk_mitigations": risk_analysis,
            "disaster_recovery": {
                "rpo": "1 hour" if complexity_score > 1 else "4 hours",  # Recovery Point Objective
                "rto": "15 minutes" if complexity_score > 1 else "1 hour",  # Recovery Time Objective
                "strategy": "Cross-region replication with automated failover"
            },
            "security_best_practices": [
                "✓ Enable VPC Flow Logs for network visibility",
                "✓ Use AWS Secrets Manager for credentials",
                "✓ Enable encryption in transit (TLS) and at rest",
                "✓ Implement API rate limiting and WAF rules",
                "✓ Set up CloudTrail for audit logging",
                "✓ Use least-privilege IAM roles"
            ],
            "monitoring_strategy": {
                "metrics": ["CPU", "Memory", "Database connections", "API latency", "Error rates"],
                "logs": "CloudWatch Logs with metric filters",
                "traces": "X-Ray for distributed tracing",
                "alarms": ["High latency > 500ms", "Error rate > 1%", "Database CPU > 80%"]
            },
            "estimated_monthly_cost_with_dr": self._calculate_dr_cost(base_design, risk_analysis)
        }
        
        return enhanced
    
    def _calculate_dr_cost(self, base_design: dict, risk_mitigations: list) -> str:
        """Calculate cost with disaster recovery"""
        # Extract base cost
        base_cost_str = base_design.get("estimated_monthly_cost", "$0").replace("$", "").replace(",", "")
        try:
            base_cost = float(base_cost_str)
        except:
            base_cost = 0
        
        # Add DR costs
        dr_overhead = base_cost * 0.3 if risk_mitigations else 0
        total = base_cost + dr_overhead
        
        return f"${int(total):,} (includes {int(dr_overhead)} DR overhead)"
    
    def _fallback_fresh_design(self, description: str) -> dict:
        """Fallback architecture design for fresh deployment"""
        lower_desc = description.lower()
        
        # Detect workload type
        is_web_app = any(x in lower_desc for x in ["web", "app", "frontend", "api"])
        is_mobile = "mobile" in lower_desc
        is_data_heavy = any(x in lower_desc for x in ["data", "analytics", "ml", "processing"])
        is_real_time = any(x in lower_desc for x in ["real-time", "streaming", "live"])
        is_simple = "simple" in lower_desc or "basic" in lower_desc
        
        # Build recommendations
        components = []
        cost_estimate = 0
        timeline = "2-3 weeks"
        
        if is_simple:
            # Minimal viable architecture
            components = [
                {
                    "name": "API Gateway",
                    "type": "compute",
                    "reason": "Serverless entry point, pay-per-use",
                    "cost": "$35"
                },
                {
                    "name": "Lambda Functions",
                    "type": "compute",
                    "reason": "Serverless logic, auto-scaling",
                    "cost": "$50"
                },
                {
                    "name": "DynamoDB",
                    "type": "database",
                    "reason": "Fully managed NoSQL, auto-scaling",
                    "cost": "$25"
                },
                {
                    "name": "S3",
                    "type": "storage",
                    "reason": "Static assets, backups",
                    "cost": "$5"
                }
            ]
            cost_estimate = 115
            timeline = "1 week"
        
        elif is_web_app:
            # Standard web application
            components = [
                {
                    "name": "CloudFront CDN",
                    "type": "network",
                    "reason": "Global edge caching, DDoS protection",
                    "cost": "$50"
                },
                {
                    "name": "Application Load Balancer",
                    "type": "network",
                    "reason": "Distribute traffic across AZs",
                    "cost": "$30"
                },
                {
                    "name": "Auto Scaling EC2",
                    "type": "compute",
                    "reason": "Handle traffic spikes, multi-AZ",
                    "cost": "$200"
                },
                {
                    "name": "RDS Multi-AZ",
                    "type": "database",
                    "reason": "Managed SQL database with failover",
                    "cost": "$150"
                },
                {
                    "name": "ElastiCache Redis",
                    "type": "caching",
                    "reason": "Session storage, object caching",
                    "cost": "$80"
                },
                {
                    "name": "S3 + CloudFront",
                    "type": "storage",
                    "reason": "Media storage with global delivery",
                    "cost": "$40"
                },
                {
                    "name": "CloudWatch + Logs",
                    "type": "monitoring",
                    "reason": "Observability, alerting",
                    "cost": "$50"
                }
            ]
            cost_estimate = 600
            timeline = "2-3 weeks"
        
        elif is_data_heavy:
            # Data processing architecture
            components = [
                {
                    "name": "S3 Data Lake",
                    "type": "storage",
                    "reason": "Centralized data repository",
                    "cost": "$100"
                },
                {
                    "name": "Glue + Athena",
                    "type": "analytics",
                    "reason": "Serverless ETL and SQL queries",
                    "cost": "$150"
                },
                {
                    "name": "Lambda Processors",
                    "type": "compute",
                    "reason": "Event-driven data processing",
                    "cost": "$80"
                },
                {
                    "name": "SQS for queuing",
                    "type": "messaging",
                    "reason": "Decouple components, ensure no data loss",
                    "cost": "$20"
                },
                {
                    "name": "Redshift (optional)",
                    "type": "warehouse",
                    "reason": "Complex analytics queries",
                    "cost": "$400 (optional)"
                }
            ]
            cost_estimate = 350
            timeline = "3-4 weeks"
        
        elif is_real_time:
            # Real-time streaming
            components = [
                {
                    "name": "Kinesis Data Streams",
                    "type": "messaging",
                    "reason": "Real-time data ingestion",
                    "cost": "$120"
                },
                {
                    "name": "Lambda for processing",
                    "type": "compute",
                    "reason": "Real-time stream processing",
                    "cost": "$100"
                },
                {
                    "name": "DynamoDB for state",
                    "type": "database",
                    "reason": "Store real-time aggregates",
                    "cost": "$80"
                },
                {
                    "name": "API Gateway + WebSocket",
                    "type": "network",
                    "reason": "Push updates to clients",
                    "cost": "$60"
                }
            ]
            cost_estimate = 360
            timeline = "2-3 weeks"
        
        else:
            # Default - balanced architecture
            components = [
                {
                    "name": "API Gateway",
                    "type": "network",
                    "reason": "API management and routing",
                    "cost": "$35"
                },
                {
                    "name": "Lambda + Auto Scaling",
                    "type": "compute",
                    "reason": "Serverless compute with auto-scaling",
                    "cost": "$100"
                },
                {
                    "name": "RDS or DynamoDB",
                    "type": "database",
                    "reason": "Data persistence with multi-AZ",
                    "cost": "$100"
                }
            ]
            cost_estimate = 235
        
        # Scalability path
        scalability_path = [
            {
                "stage": "Month 1-3: MVP",
                "users": "1K-10K",
                "actions": "Basic monitoring, manual backups"
            },
            {
                "stage": "Month 3-6: Growth",
                "users": "10K-100K",
                "actions": "Auto-scaling enabled, CDN optimized, caching tuned"
            },
            {
                "stage": "Month 6+: Scale",
                "users": "100K+",
                "actions": "Multi-region, advanced caching, database sharding"
            }
        ]
        
        return {
            "status": "designed",
            "design_type": "fresh_deployment",
            "recommended_components": components,
            "estimated_monthly_cost": f"${cost_estimate}",
            "scalability_path": scalability_path,
            "implementation_timeline": timeline,
            "design_principles": self.design_principles,
            "next_steps": [
                "1. Create AWS account and VPC",
                "2. Set up security groups and IAM roles",
                "3. Deploy core infrastructure (storage, database)",
                "4. Deploy compute layer",
                "5. Add monitoring and logging",
                "6. Test failover scenarios",
                "7. Document runbooks and procedures"
            ]
        }
