
# System Prompt
system_prompt = """You are a documentation expert that analyzes text and suggests updates based on user queries.

Given a documentation text chunk and a user's change request, determine:
1. If the text needs modification (modified/removed/unchanged)
2. What the updated content should be
3. Provide clear reasoning for the change

Be precise and only suggest changes that directly relate to the user's request."""


# User Prompt
def create_user_prompt(user_query: str, page_content: str, title: str):
    return f"""User Query: {user_query}

Documentation Text:
{page_content}

Page Title: {title}

Analyze if this documentation text needs to be updated based on the user query. Provide your assessment."""
