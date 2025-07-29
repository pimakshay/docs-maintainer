from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


class LLMManager:
    """
    Manages initialization and interaction with Gemini and embedding models.

    Provides methods to invoke the LLM with prompts and to generate embeddings for text.
    """
    def __init__(self, provider: str="google", api_key: str=None, llm_model_name="gemini-2.0-flash-exp", embedding_model_name="nomic-embed-text"):
        
        temperature = 0.0
        verbose = True

        if provider == "google":
            self.llm_model = ChatGoogleGenerativeAI(
                model=llm_model_name,
                google_api_key=api_key,
                temperature=temperature,
                verbose=verbose
            )
            self.embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model_name, 
                                          google_api_key=api_key)
        elif provider == "openai":
            self.llm_model = ChatOpenAI(
                model=llm_model_name,
                api_key=api_key,
                temperature=temperature,
                verbose=verbose
            )
            self.embeddings = OpenAIEmbeddings(model=embedding_model_name,
                                               api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")


    def invoke(self, prompt: ChatPromptTemplate, **kwargs) -> str:
        if isinstance(prompt, str):
            # If a direct string, send it as-is
            response = self.llm_model.invoke(prompt)
        else:
            # prompt: ChatPromptTemplate
            messages = prompt.format_messages(**kwargs)
            response = self.llm_model.invoke(messages)
        return response.content