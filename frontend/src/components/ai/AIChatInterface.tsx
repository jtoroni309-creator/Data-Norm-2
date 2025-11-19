'use client';

import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  Send,
  Bot,
  User,
  Sparkles,
  FileText,
  BookOpen,
  Calculator,
  AlertCircle,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Loader2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { toast } from 'sonner';

interface AIChatInterfaceProps {
  engagementId: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  context?: string;
  sources?: string[];
}

export function AIChatInterface({ engagementId }: AIChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your AI audit assistant. I can help you with:\n\n• GAAP & PCAOB standards guidance\n• Audit procedure recommendations\n• Risk assessment analysis\n• Disclosure requirements\n• Workpaper review\n• Financial analysis\n\nHow can I assist you today?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      return api.post(`/llm/chat`, {
        engagement_id: engagementId,
        message,
        context: 'audit_assistance',
      });
    },
    onSuccess: (response, userMessage) => {
      // Add assistant response
      const assistantMessage: Message = {
        id: Date.now().toString() + '-assistant',
        role: 'assistant',
        content: response.data.response || 'I apologize, but I couldn\'t generate a response. Please try again.',
        timestamp: new Date(),
        sources: response.data.sources || [],
      };
      setMessages((prev) => [...prev, assistantMessage]);
    },
    onError: () => {
      toast.error('Failed to get AI response');
      // Remove the "thinking" message
      setMessages((prev) => prev.slice(0, -1));
    },
  });

  const handleSendMessage = () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Add "thinking" message
    const thinkingMessage: Message = {
      id: Date.now().toString() + '-thinking',
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, thinkingMessage]);

    // Send to API
    sendMessageMutation.mutate(input);

    // Clear input
    setInput('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const quickPrompts = [
    {
      icon: FileText,
      label: 'ASC 606 Requirements',
      prompt: 'What are the key disclosure requirements for ASC 606 Revenue Recognition?',
    },
    {
      icon: Calculator,
      label: 'Materiality Calculation',
      prompt: 'How should I calculate materiality for this audit engagement?',
    },
    {
      icon: AlertCircle,
      label: 'Risk Assessment',
      prompt: 'What are the key fraud risks I should assess in this engagement?',
    },
    {
      icon: BookOpen,
      label: 'Audit Procedures',
      prompt: 'What substantive audit procedures should I perform for cash?',
    },
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-200px)]">
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Bot className="w-7 h-7 text-purple-600" />
          AI Audit Assistant
        </h2>
        <p className="text-gray-600 mt-1">
          Powered by your firm&apos;s knowledge base and industry standards
        </p>
      </div>

      {/* Chat Container */}
      <Card className="flex-1 flex flex-col overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}

              <div
                className={`max-w-[80%] ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                } rounded-2xl px-4 py-3`}
              >
                {message.content === '' ? (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                ) : (
                  <>
                    <div className="whitespace-pre-wrap text-sm leading-relaxed">
                      {message.content}
                    </div>

                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-xs font-semibold text-gray-600 mb-2">Sources:</p>
                        <div className="flex flex-wrap gap-2">
                          {message.sources.map((source, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {source}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {message.role === 'assistant' && message.content !== '' && (
                      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-200">
                        <button
                          onClick={() => copyToClipboard(message.content)}
                          className="p-1 hover:bg-gray-200 rounded transition-colors"
                          title="Copy"
                        >
                          <Copy className="w-3 h-3 text-gray-600" />
                        </button>
                        <button
                          className="p-1 hover:bg-gray-200 rounded transition-colors"
                          title="Helpful"
                        >
                          <ThumbsUp className="w-3 h-3 text-gray-600" />
                        </button>
                        <button
                          className="p-1 hover:bg-gray-200 rounded transition-colors"
                          title="Not helpful"
                        >
                          <ThumbsDown className="w-3 h-3 text-gray-600" />
                        </button>
                      </div>
                    )}
                  </>
                )}
              </div>

              {message.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-gray-700" />
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Prompts */}
        {messages.length === 1 && (
          <div className="px-6 pb-4">
            <p className="text-sm font-medium text-gray-700 mb-3">Quick prompts:</p>
            <div className="grid grid-cols-2 gap-2">
              {quickPrompts.map((prompt, idx) => {
                const Icon = prompt.icon;
                return (
                  <button
                    key={idx}
                    onClick={() => setInput(prompt.prompt)}
                    className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left flex items-start gap-2"
                  >
                    <Icon className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{prompt.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about GAAP standards, audit procedures, risk assessment..."
                rows={1}
                className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                style={{ minHeight: '48px', maxHeight: '120px' }}
              />
              {input.trim() && (
                <button
                  onClick={() => setInput('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              )}
            </div>
            <Button
              onClick={handleSendMessage}
              disabled={!input.trim() || sendMessageMutation.isPending}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 flex items-center gap-2"
            >
              {sendMessageMutation.isPending ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              Send
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </Card>

      {/* Capabilities */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Sparkles className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 text-sm">AI-Powered Insights</h4>
              <p className="text-xs text-gray-600 mt-1">
                Get instant answers from GAAP, PCAOB, and firm knowledge base
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <BookOpen className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 text-sm">Context-Aware</h4>
              <p className="text-xs text-gray-600 mt-1">
                Understands your engagement context and industry
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <FileText className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 text-sm">Cited Sources</h4>
              <p className="text-xs text-gray-600 mt-1">
                All responses include source references for verification
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
