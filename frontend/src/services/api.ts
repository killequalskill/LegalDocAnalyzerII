import axios, { AxiosInstance } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Document {
  id: string;
  original_filename: string;
  file_size: number;
  page_count: number;
  upload_timestamp: string;
  text_extracted: string | null;
  clauses_extracted: string | null;
}

export interface Chunk {
  id: string;
  page_number: number;
  section_name: string | null;
  clause_id: string | null;
  text: string;
}

export interface Clause {
  id: string;
  chunk_id: string;
  clause_type: string;
  reasoning: string;
  confidence: number | null;
  created_at: string;
}

export interface ReviewFlag {
  category: string;
  severity: string;
  reason: string;
  source_page: number;
  source_clause: string | null;
  source_chunk_id: string;
  extracted_value: string | null;
  is_rule_based: boolean;
}

export interface Citation {
  page_number: number;
  section_name: string | null;
  clause_id: string | null;
  chunk_id: string;
  text: string;
}

export interface AnswerResponse {
  query: string;
  answer: string;
  citations: Citation[];
  evidence_score: number;
  has_sufficient_evidence: boolean;
  evidence_notes: string;
}

export interface ClauseChange {
  change_type: string;
  section_name: string | null;
  clause_id: string | null;
  v1_text: string | null;
  v1_page: number | null;
  v2_text: string | null;
  v2_page: number | null;
  summary: string;
}

export interface ComparisonResponse {
  document_v1_id: string;
  document_v2_id: string;
  total_changes: number;
  added_count: number;
  removed_count: number;
  modified_count: number;
  unchanged_count: number;
  changes: ClauseChange[];
}

// Document endpoints
export const documentApi = {
  upload: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getDocument: async (docId: string): Promise<Document> => {
    const response = await api.get(`/documents/${docId}`);
    return response.data;
  },

  getChunks: async (docId: string): Promise<Chunk[]> => {
    const response = await api.get(`/documents/${docId}/chunks`);
    return response.data.chunks;
  },
};

// Analysis endpoints
export const analysisApi = {
  analyzeDocument: async (docId: string) => {
    const response = await api.post(`/documents/${docId}/analyze`);
    return response.data;
  },

  getClauses: async (docId: string): Promise<Clause[]> => {
    const response = await api.get(`/documents/${docId}/clauses`);
    return response.data.clauses;
  },

  getEntities: async (docId: string) => {
    const response = await api.get(`/documents/${docId}/entities`);
    return response.data.entities;
  },

  analyzeRisks: async (docId: string) => {
    const response = await api.post(`/documents/${docId}/analyze-risks`);
    return response.data;
  },

  getFlags: async (docId: string) => {
    const response = await api.get(`/documents/${docId}/flags`);
    return response.data;
  },
};

// Search/retrieval endpoints
export const searchApi = {
  retrieve: async (docId: string, query: string, topK: number = 5, method: string = 'hybrid') => {
    const response = await api.post(`/documents/${docId}/retrieve`, {
      query,
      top_k: topK,
      method,
    });
    return response.data.results;
  },
};

// QA endpoints
export const qaApi = {
  askQuestion: async (docId: string, query: string): Promise<AnswerResponse> => {
    const response = await api.post(`/documents/${docId}/query`, {
      query,
      top_k: 5,
      retrieval_method: 'hybrid',
    });
    return response.data;
  },
};

// Comparison endpoints
export const comparisonApi = {
  compare: async (docV1Id: string, docV2Id: string): Promise<ComparisonResponse> => {
    const response = await api.post('/documents/compare', {
      document_v1_id: docV1Id,
      document_v2_id: docV2Id,
    });
    return response.data;
  },
};

export default api;
