'use client';

import React, { useState } from 'react';
import DocumentCard from '../components/DocumentCard';
import { DocumentUpdate } from '../types';

export default function Home() {
  const [query, setQuery] = useState('');
  const [documents, setDocuments] = useState<DocumentUpdate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const encodedQuery = encodeURIComponent(query.trim());
      const response = await fetch(`http://localhost:8000/retrieve_relevant_documents?query=${encodedQuery}`, {
        method: 'POST',
        headers: {
          'accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setDocuments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching documents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = (document: DocumentUpdate) => {
    console.log('Approved document:', document);
    // TODO: Implement approval logic
    alert('Document approved! (Functionality to be implemented)');
  };

  const handleReject = (document: DocumentUpdate) => {
    console.log('Rejected document:', document);
    // TODO: Implement rejection logic
    setDocuments(prevDocs =>
      prevDocs.filter(doc => doc.document_metadata.chunk_id !== document.document_metadata.chunk_id)
    );
    alert('Document rejected!');
  };

  const handleEdit = (document: DocumentUpdate) => {
    console.log('Edit document:', document);
    // TODO: Implement edit logic
    alert('Edit functionality to be implemented');
  };

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
              placeholder="Ask me anything about your projects..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-gray-800"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-2xl mx-auto mb-6">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="max-w-2xl mx-auto mb-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-blue-800">Searching for relevant documents...</p>
            </div>
          </div>
        )}

        {/* Results Summary */}
        {documents.length > 0 && (
          <div className="max-w-4xl mx-auto mb-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <p className="text-gray-700">
                Found <span className="font-semibold">{documents.length}</span> document{documents.length !== 1 ? 's' : ''} that need attention
              </p>
            </div>
          </div>
        )}

        {/* Document Cards */}
        <div className="max-w-4xl mx-auto">
          {documents.map((document, index) => (
            <DocumentCard
              key={`${document.document_metadata.title}-${index}`}
              document={document}
              onApprove={handleApprove}
              onReject={() => handleReject(document)}
              onEdit={handleEdit}
            />
          ))}
        </div>

        {/* Empty State */}
        {!loading && !error && documents.length === 0 && query && (
          <div className="max-w-2xl mx-auto text-center">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <p className="text-gray-600">No documents found for your query.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 