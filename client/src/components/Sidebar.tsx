/**
 * Sidebar Component - Enhanced Version
 */

import { type FC, useState } from 'react';
import { MessageSquare, Plus, Trash2, Edit2, Check, X, Sparkles } from 'lucide-react';
import type { Conversation } from '../types';

interface SidebarProps {
  conversations: Conversation[];
  currentConversationId: string;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string) => void;
  onRenameConversation: (id: string, newTitle: string) => void;
}

export const Sidebar: FC<SidebarProps> = ({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  onRenameConversation,
}) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const startEditing = (conv: Conversation) => {
    setEditingId(conv.id);
    setEditTitle(conv.title);
  };

  const saveEdit = (id: string) => {
    if (editTitle.trim()) {
      onRenameConversation(id, editTitle.trim());
    }
    setEditingId(null);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
  };

  return (
    <div className="w-72 bg-slate-900/95 backdrop-blur-xl border-r border-slate-800/50 flex flex-col shadow-2xl">
      {/* Header */}
      <div className="p-4 border-b border-slate-800/50">
        <button
          onClick={onNewConversation}
          className="group w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white text-sm font-semibold px-4 py-3 rounded-xl transition-all duration-300 shadow-lg shadow-blue-900/20 hover:shadow-xl hover:shadow-blue-900/30 flex items-center justify-center gap-2.5 hover:scale-105 active:scale-95"
        >
          <Plus className="w-4 h-4 group-hover:rotate-90 transition-transform duration-300" />
          <span>New Conversation</span>
          <Sparkles className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
        {conversations.length === 0 ? (
          <div className="text-center py-12 px-4">
            <MessageSquare className="w-12 h-12 text-slate-700 mx-auto mb-3" />
            <p className="text-sm text-slate-500">No conversations yet</p>
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`group relative rounded-xl transition-all duration-200 ${
                conv.id === currentConversationId
                  ? 'bg-gradient-to-r from-blue-600/15 to-blue-600/10 border-2 border-blue-500/40 shadow-lg shadow-blue-900/10'
                  : 'bg-slate-800/30 hover:bg-slate-800/60 border-2 border-transparent hover:border-slate-700/50'
              }`}
            >
              {editingId === conv.id ? (
                // Edit Mode
                <div className="p-3 flex items-center gap-2">
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') saveEdit(conv.id);
                      if (e.key === 'Escape') cancelEdit();
                    }}
                    className="flex-1 bg-slate-950 text-slate-200 text-sm px-3 py-2 rounded-lg border border-slate-700 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                    autoFocus
                  />
                  <button
                    onClick={() => saveEdit(conv.id)}
                    className="p-2 hover:bg-emerald-500/20 rounded-lg transition-colors"
                    title="Save"
                  >
                    <Check className="w-4 h-4 text-emerald-500" />
                  </button>
                  <button
                    onClick={cancelEdit}
                    className="p-2 hover:bg-red-500/20 rounded-lg transition-colors"
                    title="Cancel"
                  >
                    <X className="w-4 h-4 text-red-500" />
                  </button>
                </div>
              ) : (
                // View Mode
                <div
                  onClick={() => onSelectConversation(conv.id)}
                  className="p-3 cursor-pointer flex items-start gap-3 relative overflow-hidden"
                >
                  {/* Icon */}
                  <div className={`flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center transition-all duration-200 ${
                    conv.id === currentConversationId
                      ? 'bg-gradient-to-br from-blue-600 to-blue-700 shadow-lg shadow-blue-500/20'
                      : 'bg-slate-700/50 group-hover:bg-slate-700'
                  }`}>
                    <MessageSquare className={`w-4 h-4 ${
                      conv.id === currentConversationId ? 'text-white' : 'text-slate-400'
                    }`} />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm font-semibold truncate leading-snug mb-1 ${
                      conv.id === currentConversationId ? 'text-white' : 'text-slate-300 group-hover:text-white'
                    } transition-colors`}>
                      {conv.title}
                    </p>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs ${
                        conv.id === currentConversationId ? 'text-blue-300' : 'text-slate-500'
                      }`}>
                        {conv.messages.length} {conv.messages.length === 1 ? 'message' : 'messages'}
                      </span>
                      <span className="text-xs text-slate-600">•</span>
                      <span className="text-xs text-slate-500">
                        {new Date(conv.updatedAt).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        startEditing(conv);
                      }}
                      className="p-1.5 hover:bg-blue-500/20 rounded-lg transition-all duration-200 hover:scale-110"
                      title="Rename"
                    >
                      <Edit2 className="w-3.5 h-3.5 text-blue-400" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm('Delete this conversation? This cannot be undone.')) {
                          onDeleteConversation(conv.id);
                        }
                      }}
                      className="p-1.5 hover:bg-red-500/20 rounded-lg transition-all duration-200 hover:scale-110"
                      title="Delete"
                    >
                      <Trash2 className="w-3.5 h-3.5 text-red-400" />
                    </button>
                  </div>

                  {/* Active indicator */}
                  {conv.id === currentConversationId && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-blue-500 to-blue-600 rounded-r-full"></div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800/50">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
          <span>{conversations.length} conversation{conversations.length !== 1 ? 's' : ''}</span>
        </div>
      </div>
    </div>
  );
};