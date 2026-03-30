"""
Agent for suggesting architecture for FRESH/NEW AWS deployments
Focus: Design best practices, scalability, resilience from day 1
"""
from typing import List, Dict
from agents.base_agent import BaseAgent
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

    def run(self, description: str, provider: str = "openrouter", model_id: str = None) -> dict:
        """
        Design architecture for fresh deployment
        Returns: {recommended_architecture, components, scalability_path, estimated_cost, timeline}
        """
        print(f"[{self.name}] 🆕 Designing FRESH deployment architecture...")
        print(f"[{self.name}] Principles: {', '.join(self.design_principles)}")
        
        self.provider = provider
        self.model_id = model_id
        
        # Build design prompt
        design_prompt = f"""
You are an AWS solution architect designing a NEW system from scratch.

Requirements:
{description}

Design an architecture that follows these principles:
1. **Resilience** - Handle failures gracefully
2. **Scalability** - Grow 100x without redesign
3. **Cost-efficient** - Lean infrastructure
4. **Secure** - Security best practices built-in
5. **Observable** - Monitoring/logging from day 1
6. **Maintainable** - Easy for team to manage

For the design provide:
- Main components (compute, storage, database, messaging)
- Why each component was chosen
- Scaling strategy
- Cost estimate
- Deployment order
- Timeline

Format as structured JSON with architecture array, estimated_monthly_cost, timeline_weeks.
"""
        
        # Call LLM
        llm_response = self._call_llm(
            system_prompt=self.prompt_template,
            user_input=design_prompt
        )
        
        if not llm_response:
            # Fallback design
            return self._fallback_fresh_design(description)
        
        return {
            "status": "designed",
            "design_type": "fresh_deployment",
            "architecture": llm_response,
            "principles": self.design_principles
        }
    
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
