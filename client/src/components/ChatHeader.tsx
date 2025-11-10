/**
 * @file ChatHeader.tsx
 * @description This component renders the header for the chat interface.
 * It includes the application title, a status indicator, and controls for managing the chat session.
 *
 * @props {string} selectedModel - The currently selected Ollama model.
 * @props {OllamaModel[]} models - The list of available Ollama models.
 * @props {boolean} loading - Indicates if the models are currently being loaded.
 * @props {string | null} error - An error message to display, if any.
 * @props {boolean} agentMode - Indicates whether agent mode is enabled.
 * @props {boolean} [isStreaming=false] - Indicates if a message is currently being streamed.
 * @props {(model: string) => void} onModelChange - Callback for when the selected model is changed.
 * @props {() => void} onClearConversation - Callback to clear the current conversation.
 * @props {() => void} onAgentModeToggle - Callback to toggle agent mode.
 */
import type { FC } from 'react';
import { Trash2, AlertCircle, Zap, Loader2, Sparkles, ChevronDown } from 'lucide-react';
import type { OllamaModel } from '../types';

interface ChatHeaderProps {
  selectedModel: string;
  models: OllamaModel[];
  loading: boolean;
  error: string | null;
  agentMode: boolean;
  isStreaming?: boolean;
  onModelChange: (model: string) => void;
  onClearConversation: () => void;
  onAgentModeToggle: () => void;
}

export const ChatHeader: FC<ChatHeaderProps> = ({
  selectedModel,
  models,
  loading,
  error,
  agentMode,
  isStreaming = false,
  onModelChange,
  onClearConversation,
  onAgentModeToggle,
}) => {
  return (
    <>
      {/* Header */}
      <div className="bg-slate-900/95 backdrop-blur-xl border-b border-slate-800/50 px-6 py-4 flex-shrink-0 shadow-lg">
        <div className="flex items-center justify-between">
          {/* Left: Title & Status */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              {/* Status Indicator */}
              <div className="relative">
                <div className={`w-2.5 h-2.5 rounded-full ${
                  isStreaming
                    ? 'bg-blue-500 animate-pulse'
                    : 'bg-emerald-500'
                }`}></div>
                {isStreaming && (
                  <span className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-blue-500 animate-ping opacity-75"></span>
                )}
              </div>

              {/* Title */}
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent">
                  Ollama Chat
                </h1>
                <p className="text-xs text-slate-500 font-medium mt-0.5">
                  Powered by local AI
                </p>
              </div>
            </div>

            {/* Processing Indicator */}
            {isStreaming && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-500/10 border border-blue-500/30 rounded-full animate-in fade-in slide-in-from-left-2 duration-300">
                <Loader2 className="w-3.5 h-3.5 text-blue-400 animate-spin" />
                <span className="text-xs font-medium text-blue-400">Processing...</span>
              </div>
            )}

            {/* Agent Mode Badge */}
            {agentMode && !isStreaming && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-500/10 border border-blue-500/30 rounded-full">
                <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                <span className="text-xs font-medium text-blue-400">Agent Active</span>
              </div>
            )}
          </div>

          {/* Right: Controls */}
          <div className="flex items-center gap-3">
            {/* Agent Mode Toggle */}
            <button
              onClick={onAgentModeToggle}
              className={`group relative flex items-center gap-2.5 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
                agentMode
                  ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-xl shadow-blue-900/30 hover:shadow-2xl hover:shadow-blue-900/40 hover:scale-105'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-300 border border-slate-700'
              }`}
              title="Toggle agent mode with tools"
            >
              <Zap className={`w-4 h-4 ${agentMode ? 'animate-pulse' : ''}`} />
              <span>Agent Mode</span>
              {agentMode && (
                <span className="absolute -top-1 -right-1 flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
                </span>
              )}
            </button>

            {/* Model Selector */}
            <div className="relative group">
              <select
                value={selectedModel}
                onChange={(e) => onModelChange(e.target.value)}
                className="appearance-none bg-slate-800 text-slate-200 text-sm font-medium px-4 py-2.5 pr-10 rounded-xl border border-slate-700 hover:border-slate-600 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all cursor-pointer"
                disabled={loading || models.length === 0}
              >
                {models.map((model) => (
                  <option key={model.name} value={model.name}>
                    {model.name}
                  </option>
                ))}
                {models.length === 0 && (
                  <option value="">No models available</option>
                )}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            </div>

            {/* Clear Button */}
            <button
              onClick={onClearConversation}
              className="p-2.5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-all duration-200 hover:scale-110 border border-transparent hover:border-red-500/30"
              title="Clear conversation"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-500/10 border-l-4 border-red-500 px-6 py-4 mx-6 mt-4 rounded-r-xl backdrop-blur-sm animate-in slide-in-from-top-2 duration-300">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-red-200 text-sm font-medium leading-relaxed">{error}</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
};