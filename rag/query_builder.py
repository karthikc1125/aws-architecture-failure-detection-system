def build_query(user_input):
    """
    Constructs a search query optimized for vector retrieval.
    Example:
    Input: "My S3 bucket is unavailable"
    Output: "s3 availability outage region failure"
    """
    # Simple keyword extraction or LLM-based query expansion
    return user_input + " failure outage"
