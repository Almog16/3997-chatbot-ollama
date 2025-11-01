/**
 * ToolIndicator Component - Enhanced Version
 */

import {type FC, useState, useEffect } from 'react';
import {
  Search, Calculator, Clock, BookOpen, Loader2, Globe,
  Thermometer, Calendar, Type, Info, CheckCircle2, Sparkles,
  Code, Zap, ChevronDown, ChevronUp
} from 'lucide-react';

interface ToolIndicatorProps {
  tool: string;
  args?: Record<string, any>;
  result?: string;
}

const toolConfig: Record<string, { icon: any; label: string; color: string; bgColor: string }> = {
  web_search: {
    icon: Search,
    label: 'Web Search',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10 border-blue-500/30'
  },
  get_webpage_content: {
    icon: Globe,
    label: 'Fetch Webpage',
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-500/10 border-cyan-500/30'
  },
  calculator: {
    icon: Calculator,
    label: 'Calculate',
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/10 border-purple-500/30'
  },
  unit_converter: {
    icon: Thermometer,
    label: 'Unit Conversion',
    color: 'text-orange-400',
    bgColor: 'bg-orange-500/10 border-orange-500/30'
  },
  get_current_time: {
    icon: Clock,
    label: 'Current Time',
    color: 'text-green-400',
    bgColor: 'bg-green-500/10 border-green-500/30'
  },
  get_timezone_time: {
    icon: Clock,
    label: 'Timezone Time',
    color: 'text-green-400',
    bgColor: 'bg-green-500/10 border-green-500/30'
  },
  days_between_dates: {
    icon: Calendar,
    label: 'Date Calculator',
    color: 'text-pink-400',
    bgColor: 'bg-pink-500/10 border-pink-500/30'
  },
  wikipedia_search: {
    icon: BookOpen,
    label: 'Wikipedia Search',
    color: 'text-indigo-400',
    bgColor: 'bg-indigo-500/10 border-indigo-500/30'
  },
  text_analyzer: {
    icon: Type,
    label: 'Text Analysis',
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/10 border-yellow-500/30'
  },
  encode_decode_text: {
    icon: Code,
    label: 'Encode/Decode',
    color: 'text-teal-400',
    bgColor: 'bg-teal-500/10 border-teal-500/30'
  },
  get_system_info: {
    icon: Info,
    label: 'System Info',
    color: 'text-slate-400',
    bgColor: 'bg-slate-500/10 border-slate-500/30'
  },
};

export const ToolIndicator: FC<ToolIndicatorProps> = ({ tool, args, result }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showResult, setShowResult] = useState(false);

  const config = toolConfig[tool] || {
    icon: Zap,
    label: tool,
    color: 'text-gray-400',
    bgColor: 'bg-gray-500/10 border-gray-500/30'
  };

  const Icon = config.icon;

  // Show result with animation delay
  useEffect(() => {
    if (result) {
      setTimeout(() => setShowResult(true), 150);
    }
  }, [result]);

  return (
    <div className="flex justify-start mb-3 animate-in fade-in slide-in-from-left-2 duration-300">
      <div className={`max-w-[85%] ${config.bgColor} backdrop-blur-sm border rounded-xl overflow-hidden transition-all duration-300 ${
        result ? 'shadow-lg' : ''
      }`}>
        {/* Header */}
        <div className="px-4 py-3">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className={`${config.color} relative`}>
                <Icon className="w-4 h-4" />
                {!result && (
                  <span className="absolute -top-1 -right-1 flex h-2 w-2">
                    <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${config.bgColor} opacity-75`}></span>
                    <span className={`relative inline-flex rounded-full h-2 w-2 ${config.color.replace('text-', 'bg-')}`}></span>
                  </span>
                )}
              </div>
              <div>
                <span className={`text-sm font-medium ${config.color}`}>
                  {config.label}
                </span>
                {!result && (
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <Loader2 className={`w-3 h-3 animate-spin ${config.color} opacity-70`} />
                    <span className="text-xs text-slate-500">Processing...</span>
                  </div>
                )}
                {showResult && (
                  <div className="flex items-center gap-1.5 mt-0.5 animate-in fade-in duration-300">
                    <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                    <span className="text-xs text-emerald-500 font-medium">Completed</span>
                  </div>
                )}
              </div>
            </div>

            {/* Expand/Collapse button */}
            {(args || result) && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-1.5 hover:bg-slate-700/50 rounded-lg transition-colors"
                aria-label={isExpanded ? 'Collapse' : 'Expand'}
              >
                {isExpanded ? (
                  <ChevronUp className="w-4 h-4 text-slate-400" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-slate-400" />
                )}
              </button>
            )}
          </div>
        </div>

        {/* Expandable Content */}
        {isExpanded && (
          <div className="px-4 pb-3 space-y-3 animate-in slide-in-from-top-2 duration-200">
            {/* Arguments */}
            {args && Object.keys(args).length > 0 && (
              <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-3.5 h-3.5 text-slate-400" />
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                    Parameters
                  </span>
                </div>
                <div className="space-y-1.5">
                  {Object.entries(args).map(([key, value]) => (
                    <div key={key} className="flex items-start gap-2 text-xs">
                      <span className="text-slate-500 font-medium min-w-[80px]">{key}:</span>
                      <span className="text-slate-300 flex-1 break-words font-mono">
                        {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Result */}
            {result && (
              <div className="bg-slate-900/50 rounded-lg p-3 border-l-2 border-emerald-500 animate-in fade-in duration-300">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  <span className="text-xs font-semibold text-emerald-500 uppercase tracking-wide">
                    Result
                  </span>
                </div>
                <div className="text-sm text-slate-300 leading-relaxed">
                  {result.length > 300 ? (
                    <>
                      <p className="whitespace-pre-wrap break-words">
                        {result.substring(0, 300)}...
                      </p>
                      <p className="text-xs text-slate-500 mt-2 italic">
                        ({result.length} characters total)
                      </p>
                    </>
                  ) : (
                    <p className="whitespace-pre-wrap break-words">{result}</p>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};