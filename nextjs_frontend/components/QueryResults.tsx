'use client';

import React from 'react';
import DocumentCard from './DocumentCard';
import { QueryItem, DocumentUpdate } from '../types';
import { useApprovedDocuments } from '../contexts/ApprovedDocumentsContext';

interface QueryResultsProps {
  query: QueryItem;
  onBack: () => void;
  onDiscard: (queryId: string) => void;
}

export default function QueryResults({ query, onBack, onDiscard }: QueryResultsProps) {
  const { approvedDocuments, addApprovedDocument } = useApprovedDocuments();

  const handleApprove = (document: DocumentUpdate) => {
    console.log('Approved document:', document);
    addApprovedDocument(document);
    alert('Document approved! You can review all approved documents in the Final Review page.');
  };

  const handleReject = (document: DocumentUpdate) => {
    console.log('Rejected document:', document);
    alert('Document rejected!');
  };

  const handleEdit = (document: DocumentUpdate) => {
    console.log('Edited document:', document);
    alert('Document edited successfully!');
  };

  const handleDiscard = () => {
    if (confirm('Are you sure you want to discard this query and its results?')) {
      onDiscard(query.id);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Query Results
              </h1>
              <p className="text-lg text-gray-600">
                &ldquo;{query.query}&rdquo;
              </p>
              <p className="text-sm text-gray-500">
                Completed at {query.completedAt?.toLocaleString()}
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={onBack}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
              >
                ← Back to Queries
              </button>
              <button
                onClick={handleDiscard}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
              >
                ❌ Discard Query
              </button>
            </div>
          </div>
        </div>

        {/* Results Summary */}
        {query.documents && query.documents.length > 0 && (
          <div className="max-w-4xl mx-auto mb-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <p className="text-gray-700">
                Found <span className="font-semibold">{query.documents.length}</span> document{query.documents.length !== 1 ? 's' : ''} that need attention
              </p>
            </div>
          </div>
        )}

        {/* Document Cards */}
        <div className="max-w-4xl mx-auto">
          {query.documents && query.documents.length > 0 ? (
            query.documents.map((document, index) => (
              <DocumentCard
                key={`${document.document_metadata.chunk_id}-${index}`}
                document={document}
                onApprove={handleApprove}
                onReject={() => handleReject(document)}
                onEdit={handleEdit}
              />
            ))
          ) : (
            <div className="text-center py-12">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                <p className="text-gray-600">No documents found for this query.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
