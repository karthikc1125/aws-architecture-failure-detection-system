# Two-Part Analysis System

## Overview

The architecture analysis system now provides **two specialized analysis paths** instead of a single generic endpoint:

### 1. **Deployed System Analysis** (`/api/analyze/deployed`)
- **Use Case**: Analyze already-deployed AWS architectures in production
- **Focus**: Identifying current issues, bottlenecks, and optimization opportunities
- **Output**: Issues list, risk assessment, optimization recommendations
- **Users**: DevOps teams, AWS architects reviewing existing systems

### 2. **Fresh Deployment Design** (`/api/analyze/fresh`)
- **Use Case**: Design optimal architectures for new/greenfield projects
- **Focus**: Best practices, scalability, resilience from day 1
- **Output**: Recommended components, implementation phases, cost estimates
- **Users**: Solution architects, startup founders, project leads planning new systems

---

## API Endpoints

### Deployed System Analysis

```
POST /api/analyze/deployed
Content-Type: application/json

{
  "description": "Your current architecture description",
  "provider": "openrouter",
  "model_id": "google/gemini-2.0-flash-exp:free"
}
```

**Response:**
```json
{
  "status": "optimized",
  "analysis_type": "deployed_optimization",
  "issues": [
    {
      "issue": "Single RDS Instance - No Multi-AZ",
      "severity": "High",
      "cost_impact": "Low cost but high risk",
      "optimization": "Enable Multi-AZ for $100-200/month more, massive reliability gain"
    }
  ],
  "quick_wins": [...],
  "total_potential_savings": "20-40% of infrastructure costs",
  "implementation_effort": "1-2 weeks for full optimization"
}
```

### Fresh Deployment Design

```
POST /api/analyze/fresh
Content-Type: application/json

{
  "description": "Your project requirements",
  "provider": "openrouter",
  "model_id": "google/gemini-2.0-flash-exp:free"
}
```

**Response:**
```json
{
  "status": "designed",
  "design_type": "fresh_deployment",
  "recommended_components": [
    {
      "name": "API Gateway",
      "type": "network",
      "reason": "API management and routing",
      "cost": "$35"
    },
    ...
  ],
  "estimated_monthly_cost": "$235",
  "scalability_path": [...],
  "implementation_timeline": "2-3 weeks",
  "design_principles": [...],
  "next_steps": [...]
}
```

---

## Implementation Details

### Agent Classes

#### `DeployedArchitectureAgent` (`agents/deployed_architecture_agent.py`)
- Analyzes existing AWS architectures
- Identifies cost optimization opportunities
- Detects performance bottlenecks
- Provides security and compliance recommendations
- Focus areas:
  - Cost optimization
  - Performance bottlenecks
  - Security vulnerabilities
  - Operational efficiency
  - Redundancy gaps
  - Compliance issues

#### `FreshDeploymentAgent` (`agents/fresh_deployment_advisor_agent.py`)
- Designs architectures for new projects
- Recommends AWS services based on requirements
- Plans scalability from day 1
- Provides implementation timelines and cost estimates
- Design principles:
  - Design for failure from day 1
  - Multi-AZ availability
  - Auto-scaling readiness
  - Cost optimization built-in
  - Security by default
  - Observability from start

### System Prompts

**Deployed Agent Prompt** (`agents/prompts/deployed_agent.txt`)
- Focuses on analyzing existing systems
- Prioritizes minimal-disruption improvements
- Emphasizes quick wins and cost savings
- Considers operational constraints

**Fresh Agent Prompt** (`agents/prompts/fresh_agent.txt`)
- Focuses on designing from scratch
- Applies AWS best practices
- Plans for 10x growth without redesign
- Balances cost, performance, and resilience

---

## Frontend

The web UI provides a tabbed interface at `/analyze`:

### Tab 1: Analyze Deployed System
- Input field for current architecture description
- Button: "📊 Analyze Current System"
- Displays: Health score, issues, risks, optimization opportunities

### Tab 2: Design Fresh Deployment
- Input field for project requirements
- Button: "🏗️ Design Architecture"
- Displays: Components, phases, cost estimates, scalability path

---

## Example Usage

### Deployed System Analysis
```bash
curl -X POST http://localhost:8000/api/analyze/deployed \
  -H "Content-Type: application/json" \
  -d '{
    "description": "We have 3 EC2 instances behind ALB with RDS master-slave, API Gateway with Lambda for triggers, S3 for static files, but experiencing timeouts during peak hours",
    "provider": "openrouter",
    "model_id": "google/gemini-2.0-flash-exp:free"
  }'
```

### Fresh Deployment Design
```bash
curl -X POST http://localhost:8000/api/analyze/fresh \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Building a real-time collaboration platform, 1M concurrent users, GDPR compliance needed, 50M requests/day",
    "provider": "openrouter",
    "model_id": "google/gemini-2.0-flash-exp:free"
  }'
```

---

## When to Use Each

### Use Deployed Analysis When:
- ✅ You have existing AWS infrastructure in production
- ✅ You want to optimize costs and performance
- ✅ You need to identify security vulnerabilities
- ✅ You want to improve system reliability
- ✅ You're planning incremental improvements

### Use Fresh Deployment Design When:
- ✅ Building a brand new project from scratch
- ✅ Migrating to a new cloud platform (greenfield)
- ✅ Designing optimal architecture upfront
- ✅ Planning for 10x growth from day 1
- ✅ You need cost estimates for new infrastructure

---

## Architecture Comparison

| Aspect | Deployed | Fresh |
|--------|----------|-------|
| **Input** | Existing architecture | Project requirements |
| **Focus** | Optimization | Design |
| **Constraints** | Works with existing setup | No constraints |
| **Timeline** | Quick improvements | Multi-phase rollout |
| **Risk** | Minimal disruption | Plan before build |
| **Cost** | Reduce existing spend | Estimate new spend |

---

## Error Handling

Both endpoints validate input and return appropriate HTTP status codes:

- **400 Bad Request**: Description too short (< 10 characters)
- **500 Internal Server Error**: Analysis/design failure
- **504 Gateway Timeout**: Analysis took too long

---

## Testing

Run the comprehensive test suite:

```bash
python test_two_part_analysis.py
```

This tests:
1. ✅ Deployed system analysis endpoint
2. ✅ Fresh deployment design endpoint
3. ✅ Invalid input handling

---

## Future Enhancements

- [ ] Save analysis results to database
- [ ] Generate PDF reports
- [ ] Compare multiple deployment scenarios
- [ ] Export as Terraform/CloudFormation templates
- [ ] Integration with AWS Well-Architected Review
- [ ] Multi-region analysis
- [ ] Cost projection over time
- [ ] Security assessment scoring
