from rules.service_catalog import SERVICES

# Deterministic Rules: Mitigation Strategy -> Recommended Service(s)
MITIGATION_MAPPING = {
    # Reliability
    "async_queue": ["SQS", "EventBridge"],
    "buffer": ["SQS", "Kinesis"],
    "circuit_breaker": ["API Gateway", "App Mesh", "Step Functions"],
    "bulkhead_pattern": ["Cell-Based Architecture", "Shuffle Sharding"],
    
    # Scalability & Performance
    "cache": ["ElastiCache", "CloudFront", "DAX"],
    "auto_scaling": ["AutoScaling", "DynamoDB (On-Demand)"],
    "sharding": ["Kinesis", "DynamoDB", "Aurora Global"],
    "provisioned_concurrency": ["Lambda Provisioned Concurrency"],
    "rds_proxy": ["RDS Proxy"],
    "connection_pooling": ["RDS Proxy", "ElastiCache"],

    # Availability
    "multi_region": ["Global Accelerator", "Route53", "DynamoDB Global Tables"],
    "multi_az_deployment": ["Multi-AZ RDS", "Auto Scaling Group"],
    "load_balancer": ["ALB", "NLB"],

    # Security
    "private_subnet": ["VPC with NAT Gateway"],
    "iam_roles": ["IAM Roles for EC2/Lambda"],
    "secrets_manager": ["Secrets Manager", "Parameter Store"],
    "sse_kms": ["KMS", "S3 Default Encryption"],
    "waf": ["AWS WAF", "Shield Advanced"],
    "aws_waf": ["AWS WAF"],

    # Advanced Reliability
    "dead_letter_queue": ["SQS DLQ", "Lambda DLQ"],
    "request_coalescing": ["ElastiCache", "application-side logic"],
    "shuffle_sharding": ["Route53", "Cell-Based Architecture"],
    "step_functions": ["Step Functions (Orchestration)"],
    "event_driven_architecture": ["EventBridge", "SNS/SQS"],

    # Cost
    "aws_config_rules": ["AWS Config", "CloudWatch Events"],
    "lifecycle_policy": ["S3 Lifecycle Rules", "DLM"],

    # Operations & Data Integrity
    "aws_backup": ["AWS Backup", "DynamoDB PITR"],
    "network_firewall": ["AWS Network Firewall", "Squid Proxy"],
    "egress_filtering": ["VPC Flow Logs", "Network Firewall"],
    "acm_certificate": ["ACM", "ALB HTTPS Listener"],

    # Distributed Consensus & Data
    "quorum_consensus": ["DynamoDB", "Aurora Multi-Master", "QSP (Quorum)"],
    "s3_versioning": ["S3 Versioning", "S3 Object Locking"],
    "optimistic_concurrency": ["DynamoDB Conditional Writes"],

    # API Optimization
    "batch_api_endpoints": ["AppSync (GraphQL)", "API Gateway Batch"],
    "backpressure_mechanism": ["SQS Visibility Timeout", "Circuit Breaker"],

    # Decoupling
    "decoupling": ["EventBridge", "SNS", "SQS"],
    "static_content_offload": ["S3", "CloudFront"],

    # database & storage optimization
    "io2_provisioned_iops": ["EBS io2 Block Express"],
    "increase_volume_size": ["EBS Volume Resize"],
    "instance_store": ["EC2 Instance Store (NVMe)"],
    "read_replica_distribution": ["RDS Read Replicas", "Aurora Read Replicas"],
    "serverless_v2": ["Aurora Serverless v2"],
    "dynamodb_migration": ["DynamoDB (NoSQL Migration)"],
    "dax": ["DynamoDB Accelerator (DAX)"],

    # network scaling
    "vpc_endpoints": ["VPC Endpoints (PrivateLink)", "S3 Gateway Endpoint"],
    "ipv6_egress_gateway": ["Egress Only Internet Gateway (IPv6)"],
    "multi_nat_gateway": ["Multiple NAT Gateways (Per-AZ)"],

    # compute optimization
    "memory_tuning": ["Lambda Power Tuning", "Compute Optimizer"],
    "exponential_backoff": ["AWS SDK Retry Config", "Step Functions Retry"],
    "async_processing": ["SQS", "Lambda Async Invoke", "EventBridge"],
    "spot_fleet_interruption_handler": ["Spot Fleet", "EventBridge Rule"],
    "chaos_monkey": ["AWS FIS (Fault Injection Simulator)"],
    "glue_auto_scaling": ["Glue Auto Scaling", "Spark History Server"],
    "use_glue_worker_g2x": ["Glue G.2X Worker Type"],

    # load balancing & sticky sessions
    "disable_stickiness": ["ALB Target Group Attributes"],
    "least_outstanding_requests_algorithm": ["ALB Load Balancing Algorithm"],
    "redis_session_store": ["ElastiCache for Redis"],

    # observability & logs
    "kinesis_firehose": ["Kinesis Data Firehose"],
    "asynchronous_logging": ["CloudWatch Embedded Metrics", "Lambda Extensions"],
    
    # streaming data
    "enhanced_fan_out": ["Kinesis Enhanced Fan-Out (HTTP/2)"],
    "random_partition_key": ["Kinesis Partition Key Strategy"],
    "sqs_buffer": ["SQS Standard Queue"],

    # security & waf
    "waf_counting_mode": ["AWS WAF Count Action"],
    "bot_control_managed_rule": ["AWS WAF Bot Control"],
    "custom_whitelist_rule": ["AWS WAF IP Set"],

    # data warehouse
    "concurrency_scaling": ["Redshift Concurrency Scaling"],
    "short_query_acceleration": ["Redshift SQA"],
    "spectrum_offloading": ["Redshift Spectrum (S3)"],

    # kubernetes & containers
    "init_container_dependency_check": ["Init Containers (Wait Logic)"],
    "vpc_cni_prefix_delegation": ["VPC CNI Plugin (Prefix Mode)"],
    "secondary_cidr_block": ["VPC Secondary CIDR (100.64.0.0/10)"],

    # serverless advanced
    "express_workflows": ["Step Functions Express"],
    "map_state_distributed_mode": ["Step Functions Distributed Map"],
    "max_query_depth_limit": ["AppSync Settings (Depth Limit)"],
    "appsync_cache": ["AppSync Merged API / Cache"],

    # security & iam
    "least_privilege_model": ["IAM Access Analyzer", "Permission Boundary"],
    "scp_guardrails": ["AWS Organizations SCP"],
    "block_public_access_setting": ["S3 Block Public Access (Account Level)"],
    "session_manager": ["SSM Session Manager (No SSH)"],

    # network & edge
    "private_nat_gateway": ["Private NAT Gateway"],
    "ipam_pool": ["VPC IP Address Manager (IPAM)"],
    "mtu_standardization": ["TGW MTU (8500 vs 1500)"],
    "origin_access_control": ["CloudFront OAC (Origin Access Control)"],

    # cost optimization
    "lambda_reaper": ["Lambda Scheduled Event (Cost Cleanup)"],
    "trusted_advisor_check": ["Trusted Advisor (Cost Optimization)"],
    "data_lifecycle_manager": ["Data Lifecycle Manager (DLM)"]
}

def suggest_services_for_mitigation(mitigation_strategy: str):
    """
    Returns AWS services that implement the given mitigation pattern.
    """
    # Normalize input
    strategy = mitigation_strategy.strip().lower()
    
    # Direct mapping
    if strategy in MITIGATION_MAPPING:
        return MITIGATION_MAPPING[strategy]
    
    # Fuzzy / Keyword mapping (fallback)
    if "queue" in strategy:
        return ["SQS"]
    if "cache" in strategy:
        return ["ElastiCache"]
    if "database" in strategy:
        return ["DynamoDB", "Aurora"]
        
    return []   
