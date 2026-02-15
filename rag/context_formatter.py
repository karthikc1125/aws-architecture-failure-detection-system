def format_context(documents):
    """
    Formats retrieved documents into a string for the LLM context window.
    """
    formatted = ""
    for doc in documents:
        formatted += f"Title: {doc.get('title')}\nContent: {doc.get('content')}\n---\n"
    return formatted
