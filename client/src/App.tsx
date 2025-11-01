/**
 * Main App Component with Agent Support
 * Orchestrates the entire chat application with multi-conversation and agent capabilities
 */

import { useState, useEffect } from 'react';
import type {Message, Conversation, AgentEvent, ToolCall, ToolResult} from './types';
import { Sidebar } from './components/Sidebar';
import { ChatHeader } from './components/ChatHeader';
import { ChatMessages } from './components/ChatMessages';
import { ChatInput } from './components/ChatInput';
import { ToolIndicator } from './components/ToolIndicator';

export default function App() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string>('');
  const [input, setInput] = useState('');
  const [selectedModel, setSelectedModel] = useState('qwen3:8b');
  const [agentMode, setAgentMode] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [models, setModels] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [currentToolCalls, setCurrentToolCalls] = useState<ToolCall[]>([]);
  const [currentToolResults, setCurrentToolResults] = useState<ToolResult[]>([]);

  // Get current conversation
  const currentConversation = conversations.find(c => c.id === currentConversationId);
  const messages = currentConversation?.messages || [];

  // Initialize with one conversation
  useEffect(() => {
    const initialConv: Conversation = {
      id: generateId(),
      title: 'New Chat',
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
    setConversations([initialConv]);
    setCurrentConversationId(initialConv.id);

    // Fetch models
    fetchModels();
  }, []);

  useEffect(() => {
    if (models.length === 0) return;
    const hasSelected = models.some(model => model.name === selectedModel);
    if (!hasSelected) {
      setSelectedModel(models[0].name);
    }
  }, [models, selectedModel]);

  const handleSuggestionClick = (text: string) => {
    setInput(text);
  };

  function generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  function generateTitle(firstMessage: string): string {
    const preview = firstMessage.slice(0, 50);
    return preview.length < firstMessage.length ? preview + '...' : preview;
  }

  function updateConversation(id: string, updates: Partial<Conversation>) {
    setConversations(prev =>
      prev.map(conv =>
        conv.id === id ? { ...conv, ...updates, updatedAt: Date.now() } : conv
      )
    );
  }

  const fetchModels = async () => {
    try {
      // Connect to our FastAPI backend, not Ollama directly!
      const response = await fetch('http://localhost:8000/api/models');
      if (!response.ok) throw new Error('Failed to fetch models');
      const data = await response.json();
      setModels(data.models || []);
    } catch (err) {
      setError('Could not connect to backend server');
      console.error(err);
    }
  };

  const handleNewConversation = () => {
    const newConv: Conversation = {
      id: generateId(),
      title: 'New Chat',
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
    setConversations(prev => [newConv, ...prev]);
    setCurrentConversationId(newConv.id);
  };

  const handleDeleteConversation = (id: string) => {
    setConversations(prev => prev.filter(c => c.id !== id));

    if (id === currentConversationId) {
      const remaining = conversations.filter(c => c.id !== id);
      if (remaining.length > 0) {
        setCurrentConversationId(remaining[0].id);
      } else {
        handleNewConversation();
      }
    }
  };

  const handleRenameConversation = (id: string, newTitle: string) => {
    updateConversation(id, { title: newTitle });
  };

  const clearConversation = () => {
    if (currentConversationId) {
      updateConversation(currentConversationId, {
        messages: [],
        title: 'New Chat'
      });
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isStreaming || !currentConversationId) return;

    // Check if model supports tools when Agent Mode is on
    const toolCompatibleModels =  ['qwen3', 'qwen2.5', 'deepseek', 'gpt-oss', 'gemma3','minimax-m2', 'glm'];
    const modelSupportsTools = toolCompatibleModels.some(m => selectedModel.toLowerCase().includes(m));

    if (agentMode && !modelSupportsTools) {
      setError(`⚠️ Model "${selectedModel}" doesn't support tools. Please use: qwen3:8b`);
      return;
    }

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: Date.now()
    };

    const newMessages = [...messages, userMessage];

    updateConversation(currentConversationId, {
      messages: newMessages,
      ...(messages.length === 0 && { title: generateTitle(userMessage.content) })
    });

    setInput('');
    setIsStreaming(true);
    setCurrentToolCalls([]);
    setCurrentToolResults([]);

    if (agentMode) {
      await handleAgentChat(newMessages);
    } else {
      await handleSimpleChat(newMessages);
    }
  };

  const handleAgentChat = async (newMessages: Message[]) => {
    try {
      // Add a temporary "thinking" message immediately
      const thinkingMessage: Message = {
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
      };

      updateConversation(currentConversationId, {
        messages: [...newMessages, thinkingMessage]
      });

      const response = await fetch('http://localhost:8000/api/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: selectedModel,
          messages: newMessages.map(m => ({ role: m.role, content: m.content })),
          tool_choice: 'auto',
          stream: true
        })
      });

      if (!response.ok) throw new Error('Failed to send message');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No reader available');

      let accumulatedContent = '';
      const toolCalls: ToolCall[] = [];
      const toolResults: ToolResult[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const event: AgentEvent = JSON.parse(line);

            console.log('Agent event:', event); // Debug log

            if (event.type === 'tool_call' && event.tool && event.args) {
              const toolCall = { tool: event.tool, args: event.args };
              toolCalls.push(toolCall);
              setCurrentToolCalls([...toolCalls]);
            }
            else if (event.type === 'tool_result' && event.tool && event.result) {
              const toolResult = { tool: event.tool, result: event.result };
              toolResults.push(toolResult);
              setCurrentToolResults([...toolResults]);
            }
            else if (event.type === 'message' && event.content) {
              // Accumulate content for final message
              accumulatedContent = event.content;

              // Update the conversation in real-time as content comes in
              const assistantMessage: Message = {
                role: 'assistant',
                content: accumulatedContent,
                timestamp: Date.now(),
                toolCalls: toolCalls.length > 0 ? toolCalls : undefined,
                toolResults: toolResults.length > 0 ? toolResults : undefined,
              };

              updateConversation(currentConversationId, {
                messages: [...newMessages, assistantMessage]
              });
            }
            else if (event.type === 'done') {
              // Create final message with all accumulated data
              if (accumulatedContent) {
                const assistantMessage: Message = {
                  role: 'assistant',
                  content: accumulatedContent,
                  timestamp: Date.now(),
                  toolCalls: toolCalls.length > 0 ? toolCalls : undefined,
                  toolResults: toolResults.length > 0 ? toolResults : undefined,
                };

                updateConversation(currentConversationId, {
                  messages: [...newMessages, assistantMessage]
                });
              }

              setIsStreaming(false);
              setCurrentToolCalls([]);
              setCurrentToolResults([]);
            }
            else if (event.type === 'error') {
              setError(event.content || 'An error occurred');
              setIsStreaming(false);
            }
          } catch (e) {
            console.error('Error parsing JSON:', e, 'Line:', line);
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsStreaming(false);
    }
  };

  const handleSimpleChat = async (newMessages: Message[]) => {
    try {
      // Use our backend, not Ollama directly!
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: selectedModel,
          messages: newMessages.map(m => ({ role: m.role, content: m.content })),
          stream: true
        })
      });

      if (!response.ok) throw new Error('Failed to send message');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No reader available');

      let accumulatedContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const json = JSON.parse(line);
            if (json.message?.content) {
              accumulatedContent += json.message.content;

              const assistantMessage: Message = {
                role: 'assistant',
                content: accumulatedContent,
                timestamp: Date.now()
              };

              updateConversation(currentConversationId, {
                messages: [...newMessages, assistantMessage]
              });
            }
            if (json.done) {
              setIsStreaming(false);
            }
          } catch (e) {
            console.error('Error parsing JSON:', e);
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsStreaming(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-950 flex overflow-hidden">
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={setCurrentConversationId}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        onRenameConversation={handleRenameConversation}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        <ChatHeader
          selectedModel={selectedModel}
          models={models}
          loading={false}
          error={error}
          agentMode={agentMode}
          isStreaming={isStreaming}
          onModelChange={setSelectedModel}
          onClearConversation={clearConversation}
          onAgentModeToggle={() => setAgentMode(!agentMode)}
        />

        <div className="flex-1 overflow-y-auto px-6 py-6 min-h-0 bg-slate-950">
          <ChatMessages
            messages={messages}
            isStreaming={isStreaming}
            selectedModel={selectedModel}
            onSuggestionClick={handleSuggestionClick}
          />

          {/* Show active tool indicators */}
          {isStreaming && agentMode && (
            <>
              {currentToolCalls.map((toolCall, idx) => (
                <ToolIndicator
                  key={idx}
                  tool={toolCall.tool}
                  args={toolCall.args}
                  result={currentToolResults.find(r => r.tool === toolCall.tool)?.result}
                />
              ))}
            </>
          )}
        </div>

        <ChatInput
          input={input}
          isStreaming={isStreaming}
          modelsAvailable={models.length > 0}
          onInputChange={setInput}
          onSend={handleSend}
        />
      </div>
    </div>
  );
}
