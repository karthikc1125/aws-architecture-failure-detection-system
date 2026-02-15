from typing import List, Dict, Set, Any
from pydantic import BaseModel

class ServiceNode(BaseModel):
    id: str
    type: str  # lambda, s3, dynamodb, etc.
    properties: Dict[str, Any] = {}
    redundancy_level: int = 1  # 1=Single AZ, 2=Multi AZ, etc.

class ServiceEdge(BaseModel):
    source: str
    target: str
    interaction: str  # sync, async, stream, read, write

class ArchitectureGraph:
    def __init__(self):
        self.nodes: Dict[str, ServiceNode] = {}
        self.edges: List[ServiceEdge] = []
        self.adjacency: Dict[str, List[str]] = {}

    def add_node(self, node_id: str, node_type: str, props: dict = None):
        node_id = node_id.lower().strip()
        if node_id not in self.nodes:
            self.nodes[node_id] = ServiceNode(
                id=node_id,
                type=node_type.lower(),
                properties=props or {}
            )
            self.adjacency[node_id] = []

    def add_edge(self, source: str, target: str, interaction: str = "unknown"):
        source = source.lower().strip()
        target = target.lower().strip()
        
        # Auto-create nodes if missing (inference)
        if source not in self.nodes:
            self.add_node(source, "unknown")
        if target not in self.nodes:
            self.add_node(target, "unknown")

        edge = ServiceEdge(source=source, target=target, interaction=interaction)
        self.edges.append(edge)
        self.adjacency[source].append(target)

    def detect_cycles(self) -> List[List[str]]:
        """Detects circular dependencies (infinite loops) using DFS."""
        cycles = []
        visited = set()
        path = []
        path_set = set()

        def dfs(u):
            visited.add(u)
            path.append(u)
            path_set.add(u)

            for v in self.adjacency.get(u, []):
                if v not in visited:
                    dfs(v)
                elif v in path_set:
                    # Cycle found! Extract the cycle path
                    cycle_start = path.index(v)
                    cycles.append(path[cycle_start:].copy())

            path.pop()
            path_set.remove(u)

        for node in self.nodes:
            if node not in visited:
                dfs(node)
                
        return cycles

    def detect_spof(self) -> List[str]:
        """Detects Single Points of Failure (High centrality, Low redundancy)."""
        spof_candidates = []
        
        # Calculate In-Degree (Fan-In)
        in_degree = {n: 0 for n in self.nodes}
        for e in self.edges:
            in_degree[e.target] += 1
            
        for node_id, node in self.nodes.items():
            # Criteria: High dependency (In-Degree > 1) AND Low Redundancy
            if in_degree[node_id] > 1 and node.redundancy_level == 1:
                # Exclude managed services that are inherently HA (S3, DynamoDB, SQS)
                if node.type not in ["s3", "dynamodb", "sqs", "sns", "kinesis", "step_functions", "route53"]:
                    spof_candidates.append(node_id)
                    
        return spof_candidates

    def detect_bottlenecks(self) -> List[str]:
        """Detects resource bottlenecks (High Fan-In to Compute/Database)."""
        bottlenecks = []
        in_degree = {n: 0 for n in self.nodes}
        for e in self.edges:
            in_degree[e.target] += 1
            
        for node_id, count in in_degree.items():
            node = self.nodes[node_id]
            if count >= 3 and node.type in ["lambda", "ec2", "rds"]:
                bottlenecks.append(node_id)
                
        return bottlenecks
