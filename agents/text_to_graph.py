import re
from typing import List, Tuple
from agents.graph_engine import ArchitectureGraph

AWS_SERVICES = {
    # Compute
    "lambda": ["lambda", "function", "serverless", "function_url"],
    "ec2": ["ec2", "instance", "vm", "server", "cluster"],
    "fargate": ["fargate", "container", "task"],
    "eks": ["eks", "kubernetes", "pod", "nodes"],
    "batch": ["batch", "job"],
    
    # Storage
    "s3": ["s3", "bucket", "object_storage"],
    "efs": ["efs", "nfs", "mount"],
    "ebs": ["ebs", "volume", "disk"],
    
    # Database
    "dynamodb": ["dynamodb", "table", "ddb", "nosql"],
    "rds": ["rds", "postgres", "mysql", "aurora", "database", "sql"],
    "elasticache": ["elasticache", "redis", "memcached", "cache"],
    "neptune": ["neptune", "graph"],
    
    # Integration
    "sqs": ["sqs", "queue", "message"],
    "sns": ["sns", "topic", "notification"],
    "kinesis": ["kinesis", "stream", "shard"],
    "step_functions": ["step_functions", "statemachine", "workflow"],
    "eventbridge": ["eventbridge", "bus", "rule"],
    
    # Networking
    "api_gateway": ["api_gateway", "apigw", "endpoint", "rest_api"],
    "cloudfront": ["cloudfront", "distribution", "cdn"],
    "alb": ["alb", "load_balancer", "elb"],
    "route53": ["route53", "dns", "record"],
}

INTERACTION_VERBS = [
    ("triggers", "trigger"),
    ("calls", "sync"),
    ("invokes", "sync"),
    ("writes to", "write"),
    ("reads from", "read"),
    ("sends to", "async"),
    ("publishes to", "async"),
    ("stores in", "storage"),
    ("fetches from", "read"),
    ("queries", "read"),
    ("connected to", "connect"),
]

class TextToGraphParser:
    def __init__(self):
        self.services = AWS_SERVICES
        self.verbs = INTERACTION_VERBS

    def parse(self, description: str) -> ArchitectureGraph:
        """Parses natural language into a structured Graph."""
        graph = ArchitectureGraph()
        
        # 1. Identify Nodes (Services) - Multi-pass approach
        sentences = re.split(r'[.!?\n]', description)
        
        for sentence in sentences:
            sentence = sentence.lower().strip()
            if not sentence: continue
            
            # Temporary list to store candidate matches before deduping
            candidates = []
            
            for svc_type, keywords in self.services.items():
                for kw in keywords:
                    # Search for ALL occurrences of this keyword
                    for match in re.finditer(re.escape(kw), sentence):
                        # Logic to extract full name around this match
                        # We use the match position to extract context
                        start, end = match.span()
                        
                        # Extract 3 words before and after to find the name
                        # This is a heuristic window
                        window = sentence[max(0, start-30):min(len(sentence), end+30)]
                        
                        svc_name = "generic"
                        match_composite = re.search(r'\b(\w*' + re.escape(kw) + r'\w*)\b', sentence)
                        
                        # Re-implement strategies relative to this specific match index would be complex 
                        # simpler strategy: just capture the word containing match
                        
                        # Find the word containing this keyword instance
                        # Expand strictly from match index
                        word_start = start
                        while word_start > 0 and sentence[word_start-1].isalnum():
                            word_start -= 1
                        word_end = end
                        while word_end < len(sentence) and sentence[word_end].isalnum():
                            word_end += 1
                        
                        full_word = sentence[word_start:word_end]
                        
                        # Look for name adjacent to this word
                        # e.g. "OrderService Lambda" -> full_word="lambda". Look previous word.
                        
                        # Previous word
                        prev_word = ""
                        prev_end = word_start - 1
                        while prev_end > 0 and sentence[prev_end].isspace(): prev_end -= 1
                        if prev_end >= 0:
                            prev_start = prev_end
                            while prev_start > 0 and sentence[prev_start-1].isalnum(): prev_start -= 1
                            prev_word = sentence[prev_start:prev_end+1]
                        
                        # Next word
                        next_word = ""
                        next_start = word_end + 1
                        while next_start < len(sentence) and sentence[next_start].isspace(): next_start += 1
                        if next_start < len(sentence):
                            next_end = next_start
                            while next_end < len(sentence) and sentence[next_end].isalnum(): next_end += 1
                            next_word = sentence[next_start:next_end]
                        
                        stop_words = ["the", "a", "an", "this", "that", "my", "same", "single", "all", "is", "of", "to", "in", "by", "and"]
                        
                        svc_name = "generic"
                        if full_word != kw and full_word not in stop_words:
                             svc_name = full_word
                        elif prev_word and prev_word not in stop_words:
                             svc_name = prev_word
                        elif next_word and next_word not in stop_words:
                             svc_name = next_word
                        else:
                             svc_name = f"generic_{start}"

                        candidates.append({
                            "type": svc_type,
                            "name": svc_name,
                            "start": start,
                            "end": end,
                            "kw": kw
                        })

            # Dedup candidates
            # If two candidates overlap significantly, pick the longest one or specific type
            # Sort by start position
            candidates.sort(key=lambda x: x["start"])
            
            final_nodes = []
            used_indices = set()
            
            for c in candidates:
                # Check overlap (very simple check: if start index is close to used index)
                is_overlap = False
                for i in range(c["start"], c["end"]):
                    if i in used_indices:
                        is_overlap = True
                        break
                
                if not is_overlap:
                    # Add to graph
                    clean_name = c["name"].lower()
                    for suffix in ["lambda", "function", "queue", "topic", "table", "bucket", "db", "database", "service", "sqs", "sns", "s3", "dynamodb", "rds"]:
                        clean_name = clean_name.replace(suffix, "")
                    clean_name = clean_name.strip(" _")
                    if not clean_name: clean_name = c["name"]
                    
                    node_id = f"{c['type']}_{clean_name}"
                    graph.add_node(node_id, c["type"])
                    final_nodes.append((c["start"], node_id, c["type"]))
                    
                    # Mark indices as used
                    for i in range(c["start"], c["end"] + 5): # +5 buffer/margin
                        used_indices.add(i)

            # 2. Identify Edges
            final_nodes.sort(key=lambda x: x[0])
            
            if len(final_nodes) >= 2:
                for i in range(len(final_nodes) - 1):
                    _, source_id, source_type = final_nodes[i]
                    _, target_id, target_type = final_nodes[i+1]
                    
                    # Determine interaction type
                    interaction = "unknown"
                    for verb, i_type in self.verbs:
                        if verb in sentence:
                            interaction = i_type
                            break
                    
                    graph.add_edge(source_id, target_id, interaction)
                    
        return graph

    def analyze_graph(self, graph: ArchitectureGraph) -> List[str]:
        """Runs static analysis on the graph and returns findings."""
        findings = []
        
        # Detect Cycles
        cycles = graph.detect_cycles()
        if cycles:
            for cycle in cycles:
                findings.append(f"Cycle Detected: {' -> '.join(cycle)}")
                
        # Detect SPOF
        spofs = graph.detect_spof()
        if spofs:
            for node in spofs:
                findings.append(f"Potential SPOF: {node} has high fan-in but no redundancy.")
                
        # Detect Bottlenecks
        bottlenecks = graph.detect_bottlenecks()
        if bottlenecks:
            for node in bottlenecks:
                findings.append(f"Bottleneck Detected: {node} is handling too many incoming connections.")
                
        return findings
