  /**
 * Markdown rendering utility
 * Provides simple markdown parsing for code blocks, inline code, and bold text
 */

import React from 'react';

export const renderMarkdown = (text: string): React.ReactNode[] => {
  // Split by code blocks, inline code, and bold text
  const parts = text.split(/(```[\s\S]*?```|`[^`]+`|\*\*[^*]+\*\*)/g);

  return parts.map((part, idx) => {
    // Multi-line code block
    if (part.startsWith('```') && part.endsWith('```')) {
      const code = part.slice(3, -3).trim();
      const lines = code.split('\n');
      const language = lines[0];
      const codeContent = lines.slice(1).join('\n') || code;

      return (
        <pre key={idx} className="bg-gray-900 rounded-lg p-4 my-2 overflow-x-auto">
          {language && <div className="text-gray-400 text-xs mb-2">{language}</div>}
          <code className="text-sm text-gray-100">{codeContent}</code>
        </pre>
      );
    }
    // Inline code
    else if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={idx} className="bg-gray-800 px-1.5 py-0.5 rounded text-sm">
          {part.slice(1, -1)}
        </code>
      );
    }
    // Bold text
    else if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={idx}>{part.slice(2, -2)}</strong>;
    }
    // Regular text
    return <span key={idx}>{part}</span>;
  });
};