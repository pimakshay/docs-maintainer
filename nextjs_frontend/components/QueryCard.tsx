'use client';

import React from 'react';
import { QueryItem, QueryStatus } from '../types';

interface QueryCardProps {
  query: QueryItem;
  onClick: (query: QueryItem) => void;
  onRetry?: (queryId: string) => void;
  onDiscard?: (queryId: string) => void;
}

const getStatusIcon = (status: QueryStatus) => {
  switch (status) {
    case 'completed':
      return '✅';
    case 'processing':
      return '⏳';
    case 'waiting':
      return '🕒';
    case 'error':
      return '❌';
    default:
      return '📝';
  }
};

const getStatusColor = (status: QueryStatus) => {
  switch (status) {
    case 'completed':
      return 'bg-green-50 border-green-200';
    case 'processing':
      return 'bg-blue-50 border-blue-200';
    case 'waiting':
      return 'bg-gray-50 border-gray-200';
    case 'error':
      return 'bg-red-50 border-red-200';
    default:
      return 'bg-gray-50 border-gray-200';
  }
};

const getStatusText = (status: QueryStatus) => {
  switch (status) {
    case 'completed':
      return 'Completed';
    case 'processing':
      return 'Processing';
    case 'waiting':
      return 'Waiting';
    case 'error':
      return 'Error';
    default:
      return 'Unknown';
  }
};

export default function QueryCard({ query, onClick, onRetry, onDiscard }: QueryCardProps) {
  const isClickable = query.status === 'completed';
  const showActions = query.status === 'error';
  
  return (
    <div 
      className={`p-4 rounded-lg border ${getStatusColor(query.status)} transition-all duration-200 ${
        isClickable ? 'cursor-pointer hover:shadow-md hover:scale-[1.02]' : 'cursor-default'
      }`}
      onClick={() => isClickable && onClick(query)}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-gray-800 font-medium">{query.query}</p>
          <div className="flex items-center gap-2 mt-2">
            <span className="text-2xl">{getStatusIcon(query.status)}</span>
            <span className={`text-sm font-medium ${
              query.status === 'completed' ? 'text-green-700' : 
              query.status === 'processing' ? 'text-blue-700' : 
              query.status === 'error' ? 'text-red-700' :
              'text-gray-600'
            }`}>
              {getStatusText(query.status)}
            </span>
            {query.status === 'error' && query.error && (
              <span className="text-xs text-red-600 ml-2">
                {query.error}
              </span>
            )}
          </div>
        </div>
        <div className="text-right text-xs text-gray-500">
          <div>{query.createdAt.toLocaleTimeString()}</div>
          {query.status === 'completed' && query.completedAt && (
            <div>Completed: {query.completedAt.toLocaleTimeString()}</div>
          )}
          {query.retryCount > 0 && (
            <div>Retries: {query.retryCount}</div>
          )}
        </div>
      </div>
      
      {/* Action buttons for error state */}
      {showActions && onRetry && onDiscard && (
        <div className="flex gap-2 mt-3 pt-3 border-t border-red-200">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onRetry(query.id);
            }}
            className="px-3 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600 transition-colors"
          >
            🔄 Retry
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDiscard(query.id);
            }}
            className="px-3 py-1 bg-red-500 text-white rounded text-xs hover:bg-red-600 transition-colors"
          >
            ❌ Discard
          </button>
        </div>
      )}
    </div>
  );
}
