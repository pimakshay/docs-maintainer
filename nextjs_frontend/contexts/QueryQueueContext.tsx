'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { QueryItem } from '../types';

interface QueryQueueContextType {
  queries: QueryItem[];
  addQuery: (query: QueryItem) => void;
  updateQuery: (queryId: string, updates: Partial<QueryItem>) => void;
  removeQuery: (queryId: string) => void;
  clearQueries: () => void;
  getQueryById: (queryId: string) => QueryItem | undefined;
}

const QueryQueueContext = createContext<QueryQueueContextType | undefined>(undefined);

export const useQueryQueue = () => {
  const context = useContext(QueryQueueContext);
  if (context === undefined) {
    throw new Error('useQueryQueue must be used within a QueryQueueProvider');
  }
  return context;
};

interface QueryQueueProviderProps {
  children: ReactNode;
}

export const QueryQueueProvider: React.FC<QueryQueueProviderProps> = ({ children }) => {
  const [queries, setQueries] = useState<QueryItem[]>([]);

  // Load queries from localStorage on mount
  useEffect(() => {
    try {
      const savedQueries = localStorage.getItem('queryQueue');
      if (savedQueries) {
        const parsedQueries = JSON.parse(savedQueries);
        // Convert string dates back to Date objects
        const queriesWithDates = parsedQueries.map((q: any) => ({
          ...q,
          createdAt: new Date(q.createdAt),
          completedAt: q.completedAt ? new Date(q.completedAt) : undefined,
        }));
        setQueries(queriesWithDates);
      }
    } catch (error) {
      console.error('Error loading queries from localStorage:', error);
    }
  }, []);

  // Save queries to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem('queryQueue', JSON.stringify(queries));
    } catch (error) {
      console.error('Error saving queries to localStorage:', error);
    }
  }, [queries]);

  const addQuery = (query: QueryItem) => {
    setQueries(prev => [...prev, query]);
  };

  const updateQuery = (queryId: string, updates: Partial<QueryItem>) => {
    setQueries(prev => prev.map(q => 
      q.id === queryId ? { ...q, ...updates } : q
    ));
  };

  const removeQuery = (queryId: string) => {
    setQueries(prev => prev.filter(q => q.id !== queryId));
  };

  const clearQueries = () => {
    setQueries([]);
  };

  const getQueryById = (queryId: string) => {
    return queries.find(q => q.id === queryId);
  };

  const value: QueryQueueContextType = {
    queries,
    addQuery,
    updateQuery,
    removeQuery,
    clearQueries,
    getQueryById,
  };

  return (
    <QueryQueueContext.Provider value={value}>
      {children}
    </QueryQueueContext.Provider>
  );
};
