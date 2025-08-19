export interface ModelOutput {
  change_type: "modified" | "removed" | "unchanged";
  suggested: string;
}

export interface DocumentMetadata {
  original: string
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

export type QueryStatus = 'waiting' | 'processing' | 'completed' | 'error';

export interface QueryItem {
  id: string;
  query: string;
  status: QueryStatus;
  documents?: DocumentUpdate[];
  createdAt: Date;
  completedAt?: Date;
  error?: string;
  retryCount: number;
}

export interface APIResponse {
  success: boolean;
  data?: DocumentUpdate[];
  error?: string;
} 