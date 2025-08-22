
'use client';

import React from 'react';
import ChatInterface from '../../components/ChatInterface';

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Documentation Chat
          </h1>
          <p className="text-lg text-gray-600">
            Ask questions and get instant answers about your documentation
          </p>
        </div>

        {/* Chat Interface */}
        <div className="max-w-4xl mx-auto">
          <div className="h-[600px]">
            <ChatInterface />
          </div>
        </div>

        {/* Tips */}
        <div className="max-w-4xl mx-auto mt-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 Tips for better results:</h3>
            <ul className="space-y-2 text-gray-600">
              <li>• Be specific in your questions</li>
              <li>• Ask about features, configuration, or implementation details</li>
              <li>• Reference specific functions or components when possible</li>
              <li>• Ask for examples or code snippets</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
