from typing import List, Tuple

from langchain_core.prompts import ChatPromptTemplate
from fastapi_backend.helpers.llm_manager import LLMManager


class QueryTransformer:
    """
    Preprocesses user queries to improve retrieval performance.
    """
    
    def __init__(self, llm_manager: LLMManager=None):
        self.llm_manager = llm_manager
       
        # Query improvement prompt for LLM
        self.query_improvement_prompt = ChatPromptTemplate.from_template("""
You are a query improvement expert. Your task is to improve the user's query to make it more searchable and clear while preserving the original intent.

Original query: {original_query}

Please improve this query by:
1. Fixing grammar and spelling errors
2. Adding relevant technical terms if missing
3. Making it more specific and searchable
4. Preserving the original intent
5. Keeping it concise (max 2-3 sentences)

Return only the improved query, nothing else.
""")

    def improve_query_with_llm(self, query: str) -> str:
        """
        Use LLM to improve query quality (limited usage).
        """
        if not self.llm_manager:
            return query
        
        try:
            improved_query = self.llm_manager.invoke(
                self.query_improvement_prompt,
                original_query=query
            )
            return improved_query.strip()
        except Exception as e:
            print(f"LLM query improvement failed: {e}")
            return query
