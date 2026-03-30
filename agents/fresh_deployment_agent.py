"""
FreshDeploymentAgent - Designs new architectures from scratch
Focuses on: Best practices, scalability, cost-efficiency, high availability
"""
from typing import List, Dict
from agents.base_agent import BaseAgent
from rag.retriever import Retriever
from agents.graph_engine import ArchitectureGraph, ServiceNode, ServiceEdge


class FreshDeploymentAgent(BaseAgent):
    """Designs optimal AWS architectures for new projects"""
    
    def __init__(self):
        super().__init__("FreshDeploymentAgent", "agents/prompts/fresh_deployment_agent.txt")
        self.retriever = Retriever()
        self.best_practices = self._load_best_practices()

    def _load_best_practices(self) -> Dict:
        """AWS best practices framework"""
        return {
            'reliability': [
                'Multi-AZ deployment for critical services',
                'Auto-scaling groups for load balancing',
                'Health checks and auto-recovery',
                'Multi-region failover setup',
                'Database replication and backups'
            ],
            'performance': [
                'CDN for static content (CloudFront)',
                'Caching layer (ElastiCache)',
                'Read replicas for databases',
                'Async processing with SQS/SNS',
                'Connection pooling'
            ],
            'security': [
                'VPC with public/private subnets',
                'Security groups and NACLs',
                'IAM roles with least privilege',
                'Encryption at rest and in transit',
                'Secrets management (Secrets Manager)'
            ],
            'cost_optimization': [
                'Reserved instances for stable workloads',
                'Spot instances for batch processing',
                'Auto-scaling to match demand',
                'Proper resource sizing',
                'Regular cost analysis'
            ]
        }

    def run(self, project_requirements: str) -> dict:
        """
        Designs fresh deployment architecture for:
        - Stateless web applications
        - Microservices architectures
        - Data processing pipelines
        - Real-time systems
        - Mobile/IoT backends
        """
        print(f"[{self.name}] Designing fresh deployment for: {project_requirements[:60]}...")
        
        lower_req = project_requirements.lower()
        
        # Determine project type and scale
        project_type = self._classify_project(lower_req)
        scale = self._estimate_scale(lower_req)
        
        # Generate architecture recommendation
        recommendation = self._generate_architecture(project_type, scale, lower_req)
        
        return {
            'analysis_type': 'fresh_deployment',
            'project_type': project_type,
            'estimated_scale': scale,
            'recommended_architecture': recommendation['components'],
            'design_rationale': recommendation['rationale'],
            'estimated_cost': recommendation['cost_estimate'],
            'implementation_phase': recommendation['phases'],
            'critical_considerations': recommendation['considerations'],
            'compliance_requirements': self._identify_compliance(lower_req),
            'readiness_score': 9.5  # New designs are optimized
        }

    def _classify_project(self, requirements: str) -> str:
        """Classify project type"""
        types = {
            'web': ['website', 'portal', 'dashboard', 'blog', 'cms'],
            'api': ['api', 'rest', 'graphql', 'microservice', 'backend'],
            'realtime': ['realtime', 'live', 'streaming', 'websocket', 'notification'],
            'batch': ['batch', 'etl', 'processing', 'data pipeline', 'analytics'],
            'mobile': ['mobile', 'app', 'ios', 'android', 'flutter'],
            'iot': ['iot', 'device', 'sensor', 'embedded']
        }
        
        for ptype, keywords in types.items():
            if any(kw in requirements for kw in keywords):
                return ptype
        return 'general'

    def _estimate_scale(self, requirements: str) -> dict:
        """Estimate traffic and data scale"""
        lower_req = requirements.lower()
        
        scale = {'users': 'medium', 'requests_per_day': 1000000}
        
        if any(x in lower_req for x in ['million', 'global', 'enterprise', 'scale']):
            scale = {'users': 'large', 'requests_per_day': 100000000}
        elif any(x in lower_req for x in ['startup', 'small', 'prototype']):
            scale = {'users': 'small', 'requests_per_day': 100000}
        
        return scale

    def _generate_architecture(self, project_type: str, scale: dict, requirements: str) -> dict:
        """Generate architecture based on type and scale"""
        
        base_architecture = {
            'web': {
                'components': [
                    'Route 53 (DNS)',
                    'CloudFront (CDN)',
                    'ALB (Load Balancer)',
                    'EC2 Auto Scaling or ECS',
                    'RDS (Database)',
                    'ElastiCache (Caching)',
                    'S3 (Static Assets)',
                    'CloudWatch (Monitoring)'
                ],
                'rationale': 'Highly available, scalable web application with content delivery',
                'cost_estimate': '$500-2000/month',
                'phases': ['Phase 1: VPC & Security', 'Phase 2: Compute & Storage', 'Phase 3: Database & Caching', 'Phase 4: Monitoring & Logging']
            },
            'api': {
                'components': [
                    'API Gateway',
                    'Lambda or ECS',
                    'DynamoDB or RDS',
                    'SQS/SNS (Messaging)',
                    'CloudWatch Logs',
                    'X-Ray (Tracing)',
                    'Secrets Manager'
                ],
                'rationale': 'Serverless or containerized API with async processing and security',
                'cost_estimate': '$200-1000/month',
                'phases': ['Phase 1: API Design', 'Phase 2: Database Schema', 'Phase 3: Lambda/ECS', 'Phase 4: Security & Monitoring']
            },
            'realtime': {
                'components': [
                    'AppSync or WebSocket API',
                    'Lambda',
                    'DynamoDB with Streams',
                    'Kinesis Data Streams',
                    'ElastiCache (Session)',
                    'CloudFront (Distribution)',
                    'SNS (Fan-out)'
                ],
                'rationale': 'Low-latency, event-driven architecture for real-time updates',
                'cost_estimate': '$800-3000/month',
                'phases': ['Phase 1: WebSocket Setup', 'Phase 2: Event Processing', 'Phase 3: Data Streaming', 'Phase 4: Scaling & Optimization']
            },
            'batch': {
                'components': [
                    'S3 (Data Lake)',
                    'Glue or EMR (Processing)',
                    'Lambda or Batch',
                    'RDS or Redshift (Results)',
                    'Step Functions (Orchestration)',
                    'SNS (Notifications)',
                    'CloudWatch (Monitoring)'
                ],
                'rationale': 'Scalable batch processing with orchestration and monitoring',
                'cost_estimate': '$300-1500/month',
                'phases': ['Phase 1: Data Pipeline', 'Phase 2: Processing Setup', 'Phase 3: Storage', 'Phase 4: Orchestration']
            },
            'mobile': {
                'components': [
                    'API Gateway',
                    'Cognito (Auth)',
                    'Lambda',
                    'DynamoDB or RDS',
                    'S3 (Media)',
                    'SNS (Push Notifications)',
                    'Amplify (SDK)',
                    'CloudFront (Distribution)'
                ],
                'rationale': 'Mobile-optimized backend with authentication and push notifications',
                'cost_estimate': '$400-1200/month',
                'phases': ['Phase 1: Authentication', 'Phase 2: API Backend', 'Phase 3: Media Storage', 'Phase 4: Push Notifications']
            },
            'iot': {
                'components': [
                    'IoT Core (Device Hub)',
                    'Kinesis (Data Ingestion)',
                    'Lambda (Processing)',
                    'DynamoDB (State)',
                    'TimeStream (Metrics)',
                    'S3 (Data Lake)',
                    'Greengrass (Edge)'
                ],
                'rationale': 'IoT platform with device management and edge processing',
                'cost_estimate': '$1000-5000/month',
                'phases': ['Phase 1: Device Registry', 'Phase 2: Data Ingestion', 'Phase 3: Processing', 'Phase 4: Analytics']
            }
        }
        
        arch = base_architecture.get(project_type, base_architecture['general'] if 'general' in base_architecture else base_architecture['web'])
        
        return {
            'components': arch['components'],
            'rationale': arch['rationale'],
            'cost_estimate': arch['cost_estimate'],
            'phases': arch['phases'],
            'considerations': [
                'Follow AWS Well-Architected Framework',
                'Implement comprehensive monitoring from day 1',
                'Plan for disaster recovery (RPO, RTO)',
                'Design for compliance requirements',
                'Consider multi-region strategy',
                'Implement proper logging and auditing'
            ]
        }

    def _identify_compliance(self, requirements: str) -> List[str]:
        """Identify compliance needs"""
        compliance = []
        lower_req = requirements.lower()
        
        compliance_map = {
            'HIPAA': ['healthcare', 'medical', 'patient', 'health'],
            'PCI-DSS': ['payment', 'credit card', 'financial', 'transaction'],
            'GDPR': ['eu', 'europe', 'gdpr', 'personal data'],
            'SOC 2': ['enterprise', 'soc2', 'audit', 'compliance'],
            'FedRAMP': ['government', 'federal', 'fedramp']
        }
        
        for standard, keywords in compliance_map.items():
            if any(kw in lower_req for kw in keywords):
                compliance.append(standard)
        
        return compliance if compliance else ['Standard Security Best Practices']
