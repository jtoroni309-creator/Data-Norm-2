/**
 * Natural Language Query Interface
 * COMPETITIVE DIFFERENTIATOR #8: ChatGPT-like audit analytics
 *
 * ChatGPT-style interface for asking questions about audit data
 * - Natural language to SQL conversion
 * - Real-time query execution
 * - AI-generated summaries
 * - Query history and templates
 */

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  query_result?: QueryResult;
}

interface QueryResult {
  success: boolean;
  user_query: string;
  interpreted_intent?: string;
  sql_generated?: string;
  results_count: number;
  results: any[];
  summary?: string;
  error?: string;
}

interface QueryTemplate {
  template_name: string;
  description: string;
  example_question: string;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<QueryTemplate[]>([]);
  const [showTemplates, setShowTemplates] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchQueryTemplates();
    // Welcome message
    setMessages([
      {
        id: '0',
        type: 'assistant',
        content: 'Hello! I\'m your AI audit analytics assistant. You can ask me questions about your audit data in plain English. Try asking something like "Show me all failed controls" or "What evidence is missing?"',
        timestamp: new Date()
      }
    ]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchQueryTemplates = async () => {
    try {
      const response = await axios.get('/api/v1/nl-query/suggestions');
      setTemplates(response.data);
    } catch (error) {
      console.error('Failed to fetch query templates:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);
    setShowTemplates(false);

    try {
      const response = await axios.post('/api/v1/nl-query/execute', {
        user_query: inputText
      });

      const queryResult: QueryResult = response.data;

      let assistantContent = '';
      if (queryResult.success) {
        assistantContent = queryResult.summary || `Found ${queryResult.results_count} results for your query.`;
      } else {
        assistantContent = `Sorry, I encountered an error: ${queryResult.error}`;
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: assistantContent,
        timestamp: new Date(),
        query_result: queryResult
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Sorry, I encountered an error processing your request: ${error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateClick = (template: QueryTemplate) => {
    setInputText(template.example_question);
    setShowTemplates(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const exportResults = (results: any[]) => {
    // Convert to CSV
    if (results.length === 0) return;

    const headers = Object.keys(results[0]);
    const csvContent = [
      headers.join(','),
      ...results.map(row =>
        headers.map(header => JSON.stringify(row[header] || '')).join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `query-results-${Date.now()}.csv`;
    a.click();
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">AI Audit Analytics</h1>
        <p className="text-sm text-gray-600 mt-1">Ask questions in plain English</p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {/* Query Templates */}
        {showTemplates && templates.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Try these common queries:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {templates.slice(0, 6).map((template, index) => (
                <button
                  key={index}
                  onClick={() => handleTemplateClick(template)}
                  className="text-left p-3 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors"
                >
                  <p className="text-sm font-medium text-gray-900">{template.description}</p>
                  <p className="text-xs text-gray-500 mt-1">{template.example_question}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl rounded-lg px-4 py-3 ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-900 shadow-sm border border-gray-200'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>

              {/* Query Results */}
              {message.query_result?.success && message.query_result.results.length > 0 && (
                <div className="mt-4 space-y-3">
                  {/* Intent */}
                  {message.query_result.interpreted_intent && (
                    <div className="text-xs text-gray-600 bg-gray-50 px-3 py-2 rounded">
                      <span className="font-medium">Intent:</span> {message.query_result.interpreted_intent}
                    </div>
                  )}

                  {/* Results Table */}
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 text-xs">
                      <thead className="bg-gray-50">
                        <tr>
                          {Object.keys(message.query_result.results[0]).map((key) => (
                            <th
                              key={key}
                              className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                              {key}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {message.query_result.results.slice(0, 10).map((row, rowIndex) => (
                          <tr key={rowIndex}>
                            {Object.values(row).map((value: any, colIndex) => (
                              <td key={colIndex} className="px-3 py-2 whitespace-nowrap text-sm text-gray-900">
                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Show more indicator */}
                  {message.query_result.results_count > 10 && (
                    <p className="text-xs text-gray-500 text-center">
                      Showing 10 of {message.query_result.results_count} results
                    </p>
                  )}

                  {/* Export Button */}
                  <button
                    onClick={() => exportResults(message.query_result!.results)}
                    className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded transition-colors"
                  >
                    Export to CSV
                  </button>

                  {/* SQL Query (collapsible) */}
                  {message.query_result.sql_generated && (
                    <details className="mt-2">
                      <summary className="text-xs text-gray-600 cursor-pointer hover:text-gray-900">
                        View SQL Query
                      </summary>
                      <pre className="mt-2 text-xs bg-gray-900 text-green-400 p-3 rounded overflow-x-auto">
                        {message.query_result.sql_generated}
                      </pre>
                    </details>
                  )}
                </div>
              )}

              <p className="text-xs opacity-70 mt-2">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-lg px-4 py-3 shadow-sm border border-gray-200">
              <div className="flex items-center space-x-2">
                <div className="animate-bounce w-2 h-2 bg-blue-600 rounded-full"></div>
                <div className="animate-bounce w-2 h-2 bg-blue-600 rounded-full" style={{ animationDelay: '0.1s' }}></div>
                <div className="animate-bounce w-2 h-2 bg-blue-600 rounded-full" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="flex items-end space-x-3">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about your audit data..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={3}
            disabled={loading}
          />
          <button
            onClick={handleSendMessage}
            disabled={loading || !inputText.trim()}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading ? 'Processing...' : 'Send'}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};

export default ChatInterface;
