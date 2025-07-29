'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import { useApprovedDocuments } from '../../contexts/ApprovedDocumentsContext';
import { DocumentUpdate } from '../../types';

export default function FinalReviewPage() {
  const { approvedDocuments, clearApprovedDocuments } = useApprovedDocuments();
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const handleFinalizeChanges = async () => {
    if (approvedDocuments.length === 0) {
      alert('No documents to finalize');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch('http://localhost:8000/apply_approved_changes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(approvedDocuments),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Show success message
      setShowSuccess(true);
      
      // Clear approved documents
      clearApprovedDocuments();
      
      // Navigate back to home page after a short delay
      setTimeout(() => {
        router.push('/');
      }, 2000);

    } catch (error) {
      console.error('Error finalizing changes:', error);
      alert('Error finalizing changes. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBackToHome = () => {
    router.push('/');
  };

  if (approvedDocuments.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto text-center">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <h1 className="text-2xl font-bold text-gray-900 mb-4">Final Review</h1>
              <p className="text-gray-600 mb-6">No documents have been approved for review.</p>
              <button
                onClick={handleBackToHome}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Back to Home
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Final Review
          </h1>
          <p className="text-lg text-gray-600">
            Review all approved changes before finalizing
          </p>
        </div>

        {/* Success Message */}
        {showSuccess && (
          <div className="max-w-4xl mx-auto mb-6">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-green-800 font-medium">
                You&apos;ve successfully reviewed and applied all updates.
              </p>
            </div>
          </div>
        )}

        {/* Summary */}
        <div className="max-w-4xl mx-auto mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-gray-700">
              Ready to finalize <span className="font-semibold">{approvedDocuments.length}</span> document{approvedDocuments.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>

        {/* Document Reviews */}
        <div className="max-w-6xl mx-auto mb-8">
          {approvedDocuments.map((document, index) => (
            <DocumentReviewCard key={document.document_metadata.chunk_id} document={document} index={index} />
          ))}
        </div>

        {/* Action Buttons */}
        <div className="max-w-4xl mx-auto flex justify-center gap-4">
          <button
            onClick={handleBackToHome}
            className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors font-medium"
          >
            Back to Home
          </button>
          <button
            onClick={handleFinalizeChanges}
            disabled={isSubmitting || showSuccess}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {isSubmitting ? 'Finalizing...' : 'Finalize Changes'}
          </button>
        </div>
      </div>
    </div>
  );
}

interface DocumentReviewCardProps {
  document: DocumentUpdate;
  index: number;
}

function DocumentReviewCard({ document, index }: DocumentReviewCardProps) {
  const { model_output, document_metadata } = document;

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 mb-6">
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2.5 py-0.5 rounded-full">
            Document {index + 1}
          </span>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
            model_output.change_type === 'modified' ? 'bg-yellow-100 text-yellow-800 border-yellow-200' :
            model_output.change_type === 'removed' ? 'bg-red-100 text-red-800 border-red-200' :
            'bg-green-100 text-green-800 border-green-200'
          }`}>
            {model_output.change_type}
          </span>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-1">
          {document_metadata.title}
        </h3>
        <p className="text-sm text-gray-600">
          Source:{" "}
          <a
            href={document_metadata.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline hover:text-blue-800"
          >
            {document_metadata.source_url}
          </a>
        </p>
      </div>

      {/* Content Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Original Content */}
        <div className="border border-gray-200 rounded-md p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-3 border-b border-gray-200 pb-2">
            Original Content
          </h4>
          <div className="text-sm text-gray-800 leading-relaxed max-h-64 overflow-y-auto">
            <ReactMarkdown>{document_metadata.original}</ReactMarkdown>
          </div>
        </div>

        {/* Suggested Content */}
        <div className="border border-gray-200 rounded-md p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-3 border-b border-gray-200 pb-2">
            Suggested Content
          </h4>
          <div className="text-sm text-gray-800 leading-relaxed max-h-64 overflow-y-auto">
            <ReactMarkdown>{model_output.suggested}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
} 