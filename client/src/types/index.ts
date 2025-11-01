/**
 * TypeScript type definitions for the Ollama Chat application
 * Contains all interfaces and types used across the application
 */

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  toolCalls?: ToolCall[];
  toolResults?: ToolResult[];
}

export interface ToolCall {
  tool: string;
  args: Record<string, any>;
}

export interface ToolResult {
  tool: string;
  result: string;
}

export interface OllamaModel {
  name: string;
  modified_at: string;
  size: number;
}

export interface OllamaResponse {
  model: string;
  message: {
    role: string;
    content: string;
  };
  done: boolean;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
}

export interface AgentEvent {
  type: 'status' | 'tool_call' | 'tool_result' | 'message' | 'done' | 'error';
  content?: string;
  tool?: string;
  args?: Record<string, any>;
  result?: string;
  complete?: boolean;
}