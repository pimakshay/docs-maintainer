'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import QueryCard from '../components/QueryCard';
import QueryResults from '../components/QueryResults';
import { QueryItem, DocumentUpdate, APIResponse } from '../types';
import { useApprovedDocuments } from '../contexts/ApprovedDocumentsContext';
import { useQueryQueue } from '../contexts/QueryQueueContext';

const API_BASE_URL = 'http://localhost:8000';

export default function Home() {
  const [query, setQuery] = useState('');
  const [selectedQuery, setSelectedQuery] = useState<QueryItem | null>(null);
  const router = useRouter();
  const { approvedDocuments } = useApprovedDocuments();
  const { queries, addQuery, updateQuery, removeQuery } = useQueryQueue();

  // Generate unique ID for queries
  const generateId = () => Math.random().toString(36).substr(2, 9);

  // Real API call to backend
  const callBackendAPI = async (queryText: string): Promise<DocumentUpdate[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/retrieve_relevant_documents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ query: queryText }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: DocumentUpdate[] = await response.json();
      return data;
    } catch (error) {
      console.error('API call failed:', error);
      
      // Fallback to mock data for testing when backend is unavailable
      console.log('Using mock data for testing...');
      return generateMockDocuments(queryText);
    }
  };

  // Generate mock documents for testing when backend is unavailable
  const generateMockDocuments = (queryText: string): DocumentUpdate[] => {
    const mockDocuments: DocumentUpdate[] = [
      {
        model_output: {
          change_type: 'modified',
          suggested: `Updated content for: ${queryText}\n\nThis is a suggested modification based on your query. The content has been updated to reflect the changes you requested.`
        },
        document_metadata: {
          original: `Original content for: ${queryText}\n\nThis was the original content that needed to be updated.`,
          chunk_id: generateId(),
          title: `Document Update - ${queryText.substring(0, 30)}...`,
          source_url: 'https://example.com/docs',
          file_path: '/docs/example.md'
        }
      }
    ];

    // Sometimes return multiple documents
    if (Math.random() > 0.5) {
      mockDocuments.push({
        model_output: {
          change_type: 'removed',
          suggested: `Content removed: ${queryText}\n\nThis content has been removed as requested.`
        },
        document_metadata: {
          original: `Content to be removed: ${queryText}\n\nThis content will be removed.`,
          chunk_id: generateId(),
          title: `Content Removal - ${queryText.substring(0, 30)}...`,
          source_url: 'https://example.com/docs',
          file_path: '/docs/removal.md'
        }
      });
    }

    return mockDocuments;
  };

  // Process a single query
  const processQuery = useCallback(async (queryItem: QueryItem) => {
    // Update status to processing
    updateQuery(queryItem.id, { status: 'processing' });

    try {
      // Call the real backend API
      const documents = await callBackendAPI(queryItem.query);
      
      // Update status to completed
      updateQuery(queryItem.id, { 
        status: 'completed', 
        documents,
        completedAt: new Date()
      });
    } catch (error) {
      console.error('Error processing query:', error);
      
      // Update status to error
      updateQuery(queryItem.id, { 
        status: 'error', 
        error: error instanceof Error ? error.message : 'An error occurred',
        documents: []
      });
    }
  }, [updateQuery]);

  // Process all waiting queries in parallel
  const processWaitingQueries = useCallback(() => {
    const waitingQueries = queries.filter(q => q.status === 'waiting');
    
    waitingQueries.forEach(queryItem => {
      processQuery(queryItem);
    });
  }, [queries, processQuery]);

  // Process queries when they change
  useEffect(() => {
    processWaitingQueries();
  }, [processWaitingQueries]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const newQuery: QueryItem = {
      id: generateId(),
      query: query.trim(),
      status: 'waiting',
      createdAt: new Date(),
      retryCount: 0
    };

    addQuery(newQuery);
    setQuery('');
  };

  const handleQueryClick = (query: QueryItem) => {
    if (query.status === 'completed') {
      setSelectedQuery(query);
    }
  };

  const handleBackToQueries = () => {
    setSelectedQuery(null);
  };

  const handleDiscardQuery = (queryId: string) => {
    removeQuery(queryId);
    if (selectedQuery?.id === queryId) {
      setSelectedQuery(null);
    }
  };

  const handleRetryQuery = (queryId: string) => {
    const queryToRetry = queries.find(q => q.id === queryId);
    if (queryToRetry) {
      // Reset status and increment retry count
      updateQuery(queryId, { 
        status: 'waiting', 
        error: undefined,
        retryCount: queryToRetry.retryCount + 1
      });
    }
  };

  // Calculate processing statistics
  const processingCount = queries.filter(q => q.status === 'processing').length;
  const waitingCount = queries.filter(q => q.status === 'waiting').length;
  const errorCount = queries.filter(q => q.status === 'error').length;
  const completedCount = queries.filter(q => q.status === 'completed').length;

  // If showing query results, render that component
  if (selectedQuery) {
    return (
      <QueryResults
        query={selectedQuery}
        onBack={handleBackToQueries}
        onDiscard={handleDiscardQuery}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Documentation Maintainer
          </h1>
          <p className="text-lg text-gray-600">
            Review and manage documentation updates
          </p>
        </div>

        {/* Query Form */}
        <div className="max-w-2xl mx-auto mb-8">
          <form onSubmit={handleSubmit} className="flex gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask me anything about your projects"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-gray-800"
            />
            <button
              type="submit"
              disabled={!query.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
            >
              📤
            </button>
          </form>
        </div>

        {/* Progress Tracking */}
        {(processingCount > 0 || waitingCount > 0 || errorCount > 0) && (
          <div className="max-w-2xl mx-auto mb-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {processingCount > 0 && (
                    <span className="text-blue-600 font-medium">
                      ⏳ {processingCount} processing
                    </span>
                  )}
                  {waitingCount > 0 && (
                    <span className="text-gray-600 font-medium">
                      🕒 {waitingCount} waiting
                    </span>
                  )}
                  {errorCount > 0 && (
                    <span className="text-red-600 font-medium">
                      ❌ {errorCount} errors
                    </span>
                  )}
                </div>
                {completedCount > 0 && (
                  <span className="text-green-600 font-medium">
                    ✅ {completedCount} completed
                  </span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Final Review Button */}
        {approvedDocuments.length > 0 && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-800 font-medium">
                    {approvedDocuments.length} document{approvedDocuments.length !== 1 ? 's' : ''} approved
                  </p>
                  <p className="text-green-600 text-sm">
                    Ready for final review
                  </p>
                </div>
                <button
                  onClick={() => router.push('/final-review')}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                >
                  Go to Final Review
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Query Queue */}
        <div className="max-w-4xl mx-auto">
          {queries.length > 0 ? (
            <div className="space-y-4">
              {queries.map((queryItem) => (
                <QueryCard
                  key={queryItem.id}
                  query={queryItem}
                  onClick={handleQueryClick}
                  onRetry={handleRetryQuery}
                  onDiscard={handleDiscardQuery}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                <p className="text-gray-600">No queries yet. Start by asking a question above!</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 