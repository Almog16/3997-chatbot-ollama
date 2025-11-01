/**
 * ChatInput Component
 * Multi-line support with fixed alignment
 */

import React from 'react';
import { Send, Loader2, Sparkles } from 'lucide-react';

interface ChatInputProps {
  input: string;
  isStreaming: boolean;
  modelsAvailable: boolean;
  onInputChange: (value: string) => void;
  onSend: () => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  input,
  isStreaming,
  modelsAvailable,
  onInputChange,
  onSend,
}) => {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  const canSend = input.trim() && !isStreaming && modelsAvailable;

  return (
    <div className="border-t border-slate-800/50 bg-slate-900/95 backdrop-blur-xl p-4 flex-shrink-0 shadow-2xl">
      <div className="max-w-5xl mx-auto">
        {/* Input Row */}
        <div className="flex gap-3 items-center">
          {/* Textarea */}
          <textarea
            value={input}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder={
              isStreaming
                ? "Waiting for response..."
                : "Type your message..."
            }
            className="flex-1 h-[52px] bg-slate-800/80 text-white placeholder-slate-500 rounded-2xl px-5 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/40 border border-slate-700/50 focus:border-blue-500/40 transition-all duration-200 shadow-lg hover:shadow-xl overflow-y-auto"
            disabled={!modelsAvailable}
          />

          {/* Send Button */}
          <button
            onClick={onSend}
            disabled={!canSend}
            className={`h-[52px] px-6 rounded-2xl font-semibold transition-all duration-300 flex items-center justify-center gap-2.5 shadow-lg flex-shrink-0 ${
              canSend
                ? 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white hover:shadow-2xl hover:shadow-blue-500/30 hover:scale-105 active:scale-95'
                : 'bg-slate-800 text-slate-600 cursor-not-allowed border border-slate-700/50'
            }`}
          >
            {isStreaming ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span className="hidden sm:inline">Sending</span>
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span className="hidden sm:inline">Send</span>
              </>
            )}
          </button>
        </div>

        {/* Helper Text */}
        <div className="flex items-center justify-between mt-2.5 px-1">
          <p className="text-xs text-slate-500 flex items-center gap-2">
            <Sparkles className="w-3 h-3" />
            <span>
              <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-xs">Enter</kbd> to send ·
              <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-xs ml-1">Shift + Enter</kbd> for new line
            </span>
          </p>

          {!modelsAvailable && (
            <span className="text-xs text-amber-500 font-medium">
              No models available
            </span>
          )}
        </div>
      </div>
    </div>
  );
};