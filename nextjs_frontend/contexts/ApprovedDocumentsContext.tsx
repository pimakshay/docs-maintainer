'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { DocumentUpdate } from '../types';

interface ApprovedDocumentsContextType {
  approvedDocuments: DocumentUpdate[];
  addApprovedDocument: (document: DocumentUpdate) => void;
  removeApprovedDocument: (chunkId: string) => void;
  clearApprovedDocuments: () => void;
  updateApprovedDocument: (chunkId: string, updatedDocument: DocumentUpdate) => void;
}

const ApprovedDocumentsContext = createContext<ApprovedDocumentsContextType | undefined>(undefined);

export function ApprovedDocumentsProvider({ children }: { children: ReactNode }) {
  const [approvedDocuments, setApprovedDocuments] = useState<DocumentUpdate[]>([]);

  const addApprovedDocument = (document: DocumentUpdate) => {
    setApprovedDocuments(prev => {
      // Check if document already exists
      const exists = prev.some(doc => doc.document_metadata.chunk_id === document.document_metadata.chunk_id);
      if (exists) {
        return prev;
      }
      return [...prev, document];
    });
  };

  const removeApprovedDocument = (chunkId: string) => {
    setApprovedDocuments(prev => 
      prev.filter(doc => doc.document_metadata.chunk_id !== chunkId)
    );
  };

  const clearApprovedDocuments = () => {
    setApprovedDocuments([]);
  };

  const updateApprovedDocument = (chunkId: string, updatedDocument: DocumentUpdate) => {
    setApprovedDocuments(prev => 
      prev.map(doc => 
        doc.document_metadata.chunk_id === chunkId ? updatedDocument : doc
      )
    );
  };

  return (
    <ApprovedDocumentsContext.Provider value={{
      approvedDocuments,
      addApprovedDocument,
      removeApprovedDocument,
      clearApprovedDocuments,
      updateApprovedDocument,
    }}>
      {children}
    </ApprovedDocumentsContext.Provider>
  );
}

export function useApprovedDocuments() {
  const context = useContext(ApprovedDocumentsContext);
  if (context === undefined) {
    throw new Error('useApprovedDocuments must be used within an ApprovedDocumentsProvider');
  }
  return context;
} 