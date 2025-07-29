export interface ModelOutput {
  change_type: "modified" | "removed" | "unchanged";
  original: string;
  suggested: string;
}

export interface DocumentMetadata {
  chunk_id: string
  title: string;
  source_url: string;
  file_path: string;
}

export interface DocumentUpdate {
  model_output: ModelOutput;
  document_metadata: DocumentMetadata;
}

export interface QueryRequest {
  query: string;
} 