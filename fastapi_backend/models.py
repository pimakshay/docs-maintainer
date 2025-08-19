from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(description="User query string")

class ModelOutput(BaseModel):
    change_type:str = Field(description="Mention the change type: modified, removed, unchanged")
    suggested: str = Field(description="Suggested changes to the page content")
    # remark: str = 

class DocumentMetadata(BaseModel):
    chunk_id: str = Field(description="Unique chunk ID")
    original: str = Field(description="Original page content")
    title: str = Field(description="Title of the page")
    source_url: str = Field(description="Source URL of the page")
    file_path: str = Field(description="File path of the page")
    
class DocumentUpdate(BaseModel):
    model_output: ModelOutput = Field(description="Model output")
    document_metadata: DocumentMetadata = Field(description="Document metadata")