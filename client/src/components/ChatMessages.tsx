/**
 * ChatMessages Component - Enhanced Version
 */

import React, { useRef, useEffect } from 'react';
import { Sparkles, Loader2, Zap, MessageSquare } from 'lucide-react';
import type { Message } from '../types';
import { MessageBubble } from './MessageBubble';

interface ChatMessagesProps {
  messages: Message[];
  isStreaming: boolean;
  selectedModel: string;
  onSuggestionClick?: (text: string) => void;
}

export const ChatMessages: React.FC<ChatMessagesProps> = ({
  messages,
  isStreaming,
  selectedModel,
  onSuggestionClick
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto px-6 py-8 space-y-1 min-h-0 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
      {/* Empty State */}
      {messages.length === 0 && (
        <div className="flex items-center justify-center h-full animate-in fade-in duration-500">
          <div className="text-center max-w-md">
            {/* Icon */}
            <div className="relative mx-auto mb-6 w-20 h-20">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl animate-pulse opacity-20 blur-xl"></div>
              <div className="relative w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl flex items-center justify-center shadow-2xl shadow-purple-500/50 transform hover:scale-110 transition-transform duration-300">
                <Sparkles className="w-10 h-10 text-white animate-pulse" />
              </div>
            </div>

            {/* Text */}
            <h2 className="text-2xl font-bold bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent mb-3">
              Start a Conversation
            </h2>
            <p className="text-slate-400 leading-relaxed mb-6">
              Ask me anything! I'm powered by <span className="text-purple-400 font-semibold">{selectedModel}</span>
            </p>

            {/* Suggestions */}
            <div className="grid grid-cols-1 gap-3 mt-8">
              {[
                { icon: MessageSquare, text: "Tell me a story", color: "from-blue-500 to-cyan-500" },
                { icon: Zap, text: "Help me code something", color: "from-purple-500 to-pink-500" },
                { icon: Sparkles, text: "Explain a concept", color: "from-emerald-500 to-teal-500" },
              ].map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => onSuggestionClick?.(suggestion.text)}
                  className="group relative px-6 py-4 bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 hover:border-slate-600 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-xl text-left"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${suggestion.color} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                      <suggestion.icon className="w-5 h-5 text-white" />
                    </div>
                    <span className="text-sm font-medium text-slate-300 group-hover:text-white transition-colors">
                      {suggestion.text}
                    </span>
                  </div>

                  {/* Shine effect */}
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-transparent via-white/5 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Message List */}
      {messages.map((message, idx) => {
        // Don't render empty assistant messages (they're placeholders)
        if (message.role === 'assistant' && message.content === '') {
          return null;
        }
        return <MessageBubble key={idx} message={message} />;
      })}

      {/* Typing Indicator */}
      {isStreaming && messages[messages.length - 1]?.content === '' && (
        <div className="flex justify-start mb-4 animate-in fade-in slide-in-from-left-2 duration-300">
          <div className="flex items-center gap-3">
            {/* Avatar */}
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/30">
              <Sparkles className="w-4 h-4 text-white animate-pulse" />
            </div>

            {/* Typing Animation */}
            <div className="bg-slate-800 border border-slate-700/50 rounded-2xl px-5 py-3 flex items-center gap-3 shadow-lg">
              <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
              </div>
              <span className="text-slate-400 text-sm font-medium">Thinking...</span>
            </div>
          </div>
        </div>
      )}

      {/* Auto-scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
};