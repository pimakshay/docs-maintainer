'use client';

import React from 'react';
import ReactDiffViewer from 'react-diff-viewer';
import ReactMarkdown from 'react-markdown';
import { DocumentUpdate } from '../types';

interface DocumentCardProps {
  document: DocumentUpdate;
  onApprove: (document: DocumentUpdate) => void;
  onReject: (document: DocumentUpdate) => void;
  onEdit: (document: DocumentUpdate) => void;
}

const getChangeTypeColor = (changeType: string) => {
  switch (changeType) {
    case 'modified':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'removed':
      return 'bg-red-100 text-red-800 border-red-200';
    case 'unchanged':
      return 'bg-green-100 text-green-800 border-green-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

const getChangeTypeIcon = (changeType: string) => {
  switch (changeType) {
    case 'modified':
      return '✏️';
    case 'removed':
      return '🗑️';
    case 'unchanged':
      return '✓';
    default:
      return '📄';
  }
};

// Custom renderer for markdown content in diff viewer
const renderMarkdown = (content: string) => {
  return (
    <div className="prose prose-sm max-w-none">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
};

export default function DocumentCard({ document, onApprove, onReject, onEdit }: DocumentCardProps) {
  const { model_output, document_metadata } = document;

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 mb-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            {document_metadata.title}
          </h3>
          <p className="text-sm text-gray-600 mb-2">
            Source: {document_metadata.source_url}
          </p>
          <div className="flex items-center gap-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getChangeTypeColor(model_output.change_type)}`}>
              <span className="mr-1">{getChangeTypeIcon(model_output.change_type)}</span>
              {model_output.change_type}
            </span>
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="flex flex-col gap-2 ml-4">
          <button
            onClick={() => onApprove(document)}
            className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors text-sm font-medium"
          >
            ✓ Approve
          </button>
          <button
            onClick={() => onReject(document)}
            className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors text-sm font-medium"
          >
            ✗ Reject
          </button>
          <button
            onClick={() => onEdit(document)}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm font-medium"
          >
            ✎ Edit
          </button>
        </div>
      </div>

      {/* Diff Viewer */}
      <div className="border border-gray-200 rounded-md overflow-hidden">
        <div className="max-h-96 overflow-auto">
          <ReactDiffViewer
            oldValue={model_output.original}
            newValue={model_output.suggested}
            splitView={true}
            useDarkTheme={false}
            renderContent={renderMarkdown}
            styles={{
              diffContainer: {
                preStyles: {
                  backgroundColor: '#f8f9fa',
                  color: '#333',
                  fontSize: '13px',
                  lineHeight: '1.4',
                  margin: '0',
                  padding: '8px',
                },
              },
              line: {
                padding: '4px 8px',
              },
              lineNumber: {
                color: '#999',
                backgroundColor: '#f1f3f4',
                minWidth: '40px',
                padding: '4px 8px',
              },
              diffRemoved: {
                backgroundColor: '#ffeef0',
                color: '#c53030',
              },
              diffAdded: {
                backgroundColor: '#e6ffed',
                color: '#22543d',
              },
              splitView: {
                width: '100%',
              },
            }}
          />
        </div>
      </div>
    </div>
  );
} 