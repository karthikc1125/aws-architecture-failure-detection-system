# Service Catalog: The menu of available AWS building blocks.

SERVICES = {
    "compute": {
        "Lambda": "Serverless compute, event-driven.",
        "ECS": "Container orchestration, suitable for long-running services.",
        "Fargate": "Serverless compute engine for containers.",
        "EC2": "Virtual servers in the cloud."
    },
    "messaging": {
        "SQS": "Fully managed message queuing service (Standard & FIFO).",
        "SNS": "Pub/sub messaging service.",
        "EventBridge": "Serverless event bus for building event-driven applications.",
        "Kinesis": "Real-time data streaming."
    },
    "database": {
        "DynamoDB": "NoSQL key-value database, serverless.",
        "Aurora": "Relational database built for the cloud.",
        "RDS": "Managed relational database service.",
        "ElastiCache": "In-memory caching (Redis/Memcached)."
    },
    "storage": {
        "S3": "Object storage, highly durable.",
        "EFS": "Scalable file storage for EC2.",
        "EBS": "Block storage volumes."
    },
    "network": {
        "API Gateway": "managed service for creating APIs.",
        "AppSync": "Managed GraphQL service.",
        "ALB": "Application Load Balancer.",
        "NLB": "Network Load Balancer.",
        "CloudFront": "Content Delivery Network (CDN)."
    },
    "management": {
        "CloudWatch": "Monitoring and observability.",
        "X-Ray": "Distributed tracing.",
        "AutoScaling": "Automatically adjusts capacity."
    }
}

def get_service_category(service_name):
    """Returns the category of a given service."""
    for category, services in SERVICES.items():
        if service_name in services:
            return category
    return "unknown"

