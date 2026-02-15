from vector_store.search import search_by_failure
from rag.query_builder import build_query
from rag.context_formatter import format_context

class Retriever:
    def retrieve(self, user_input: str):
        """
        Retrieves relevant context (incidents, patterns) for a given query.
        """
        print(f"Retrieving context for: {user_input}")
        
        # 1. Use QueryBuilder to parse query
        query = build_query(user_input)
        print(f"Optimized query: {query}")
        
        # 2. Call search_by_failure
        results = search_by_failure(query)
        print(f"Found {len(results)} relevant memory items.")
        
        # 3. Use ContextFormatter to format results
        formatted_context = format_context(results)
        
        return {
            "query": query,
            "raw_results": results,
            "formatted_context": formatted_context
        }
