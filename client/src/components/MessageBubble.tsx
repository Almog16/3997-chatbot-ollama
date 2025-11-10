/**
 * @file MessageBubble.tsx
 * @description This component renders a single chat message bubble.
 * It distinguishes between messages from the user and the assistant, styling them differently.
 * It also provides a button to copy the message content to the clipboard and indicates when tools are used.
 *
 * @props {Message} message - The message object to be rendered.
 */
import { type FC, useState } from 'react';
import { Copy, Check, User, Bot, Sparkles } from 'lucide-react';
import type { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: FC<MessageBubbleProps> = ({ message }) => {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Check if message has tool usage
  const hasTools = message.toolCalls && message.toolCalls.length > 0;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 group animate-in fade-in slide-in-from-bottom-2 duration-300`}>
      <div className={`max-w-[85%] flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser
            ? 'bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg shadow-blue-500/20'
            : 'bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg shadow-emerald-500/30'
        }`}>
          {isUser ? (
            <User className="w-4 h-4 text-white" />
          ) : (
            <Bot className="w-4 h-4 text-white" />
          )}
        </div>

        {/* Message Content */}
        <div className="flex-1 min-w-0">
          {/* Tool Badge */}
          {hasTools && !isUser && (
            <div className="flex items-center gap-1.5 mb-2 animate-in fade-in duration-300">
              <Sparkles className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-xs font-medium text-blue-400">
                Used {message.toolCalls!.length} tool{message.toolCalls!.length > 1 ? 's' : ''}
              </span>
            </div>
          )}

          {/* Message Bubble */}
          <div
            className={`rounded-2xl px-4 py-3 shadow-lg transition-all duration-200 bg-slate-800 text-slate-100 border border-slate-700/50 shadow-slate-900/50`}
          >
            <div className="text-[15px] leading-relaxed whitespace-pre-wrap break-words">
              {message.content}
            </div>

            {/* Tool Summary */}
            {hasTools && !isUser && message.toolCalls && (
              <div className="mt-3 pt-3 border-t border-slate-700/50">
                <div className="flex flex-wrap gap-2">
                  {message.toolCalls.map((toolCall, idx) => (
                    <div
                      key={idx}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-slate-900/50 border border-slate-600/50 rounded-full text-xs"
                    >
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                      <span className="text-slate-300 font-medium">{toolCall.tool}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Metadata */}
          <div className={`flex items-center gap-3 mt-2 px-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <span className="text-xs text-slate-500 font-medium">
              {new Date(message.timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </span>

            {/* Copy Button */}
            <button
              onClick={copyToClipboard}
              className="opacity-0 group-hover:opacity-100 transition-all duration-200 p-1.5 hover:bg-slate-800 rounded-lg text-slate-500 hover:text-slate-300 hover:scale-110"
              title="Copy message"
            >
              {copied ? (
                <Check className="w-3.5 h-3.5 text-emerald-500" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};