'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Bot,
  Send,
  X,
  Sparkles,
  FileText,
  Link as LinkIcon,
  Minimize2,
  Maximize2,
} from 'lucide-react';
import { aiService, AIChatMessage } from '@/lib/ai-service';
import { cn } from '@/lib/utils';

interface AIAssistantProps {
  context?: {
    engagement_id?: string;
    current_page?: string;
    user_role?: string;
  };
  className?: string;
}

export function AIAssistant({ context, className }: AIAssistantProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState<AIChatMessage[]>([
    {
      role: 'assistant',
      content:
        "Hello! I'm your AI audit assistant. I can help you with audit procedures, standards interpretation, risk assessment, and more. How can I assist you today?",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: AIChatMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
      context,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await aiService.chat([...messages, userMessage], context);

      const assistantMessage: AIChatMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        context: {
          suggested_actions: response.suggested_actions,
          references: response.references,
        },
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: AIChatMessage = {
        role: 'assistant',
        content: "I apologize, but I'm having trouble processing your request. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestedPrompts = [
    'How do I test journal entries for fraud?',
    'Explain PCAOB AS 1215 requirements',
    'What are the steps for risk assessment?',
    'Help me understand materiality calculation',
  ];

  return (
    <>
      {/* Floating AI Button */}
      <Button
        onClick={() => setIsOpen(true)}
        className={cn(
          'fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg z-50',
          'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700',
          className
        )}
        size="icon"
      >
        <Sparkles className="h-6 w-6 text-white" />
      </Button>

      {/* AI Assistant Dialog */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent
          className={cn(
            'transition-all duration-300',
            isExpanded ? 'max-w-4xl h-[80vh]' : 'max-w-2xl h-[600px]'
          )}
        >
          <DialogHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-r from-blue-600 to-purple-600">
                  <Bot className="h-6 w-6 text-white" />
                </div>
                <div>
                  <DialogTitle>AI Audit Assistant</DialogTitle>
                  <DialogDescription>Powered by advanced AI</DialogDescription>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsExpanded(!isExpanded)}
                >
                  {isExpanded ? (
                    <Minimize2 className="h-4 w-4" />
                  ) : (
                    <Maximize2 className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </DialogHeader>

          {/* Chat Messages */}
          <div className="flex-1 space-y-4 overflow-y-auto px-4 py-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={cn(
                  'flex',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                <div
                  className={cn(
                    'max-w-[80%] rounded-lg px-4 py-2',
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-muted'
                  )}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                  {/* Suggested Actions */}
                  {message.context?.suggested_actions && (
                    <div className="mt-3 space-y-2">
                      <p className="text-xs font-semibold opacity-70">Suggested Actions:</p>
                      {message.context.suggested_actions.map((action: any, i: number) => (
                        <Button
                          key={i}
                          variant="outline"
                          size="sm"
                          className="w-full justify-start text-xs"
                          onClick={() => action.url && (window.location.href = action.url)}
                        >
                          {action.action}
                        </Button>
                      ))}
                    </div>
                  )}

                  {/* References */}
                  {message.context?.references && (
                    <div className="mt-3 space-y-1">
                      <p className="text-xs font-semibold opacity-70">References:</p>
                      {message.context.references.map((ref: any, i: number) => (
                        <div key={i} className="flex items-center space-x-2 text-xs">
                          <LinkIcon className="h-3 w-3" />
                          <span>
                            {ref.standard} - {ref.section}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}

                  <p className="mt-1 text-xs opacity-50">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[80%] rounded-lg bg-muted px-4 py-2">
                  <div className="flex space-x-2">
                    <div className="h-2 w-2 animate-bounce rounded-full bg-gray-500"></div>
                    <div className="h-2 w-2 animate-bounce rounded-full bg-gray-500 [animation-delay:0.2s]"></div>
                    <div className="h-2 w-2 animate-bounce rounded-full bg-gray-500 [animation-delay:0.4s]"></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Prompts (show when no messages) */}
          {messages.length === 1 && (
            <div className="px-4">
              <p className="mb-2 text-xs font-semibold text-muted-foreground">
                Try asking:
              </p>
              <div className="grid grid-cols-2 gap-2">
                {suggestedPrompts.map((prompt, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="justify-start text-xs"
                    onClick={() => setInputValue(prompt)}
                  >
                    {prompt}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="flex items-center space-x-2 px-4 pb-4">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about auditing..."
              className="flex-1"
              disabled={isLoading}
            />
            <Button
              onClick={handleSend}
              disabled={!inputValue.trim() || isLoading}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
