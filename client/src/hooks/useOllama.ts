/**
 * Custom React hook for Ollama API integration
 * Handles model fetching, message streaming, and error states
 */

import { useState, useCallback } from 'react';
import type {Message, OllamaModel, OllamaResponse} from '../types';

export const useOllama = (baseUrl: string = 'http://localhost:11434') => {
  const [models, setModels] = useState<OllamaModel[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch available Ollama models from the API
   */
  const fetchModels = useCallback(async () => {
    try {
      const response = await fetch(`${baseUrl}/api/tags`);
      if (!response.ok) throw new Error('Failed to fetch models');
      const data = await response.json();
      setModels(data.models || []);
    } catch (err) {
      setError('Could not connect to Ollama. Make sure it\'s running on localhost:11434');
      console.error(err);
    }
  }, [baseUrl]);

  /**
   * Send a message to Ollama with streaming support
   * @param messages - Array of conversation messages
   * @param model - The Ollama model to use
   * @param onChunk - Callback fired as content streams in
   * @param onComplete - Callback fired when streaming completes
   */
  const sendMessage = useCallback(async (
    messages: Message[],
    model: string,
    onChunk: (content: string) => void,
    onComplete: () => void
  ) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${baseUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model,
          messages: messages.map(m => ({ role: m.role, content: m.content })),
          stream: true
        })
      });

      if (!response.ok) throw new Error('Failed to send message');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No reader available');

      let accumulatedContent = '';

      // Read the streaming response
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());

        // Parse each line as JSON (NDJSON format)
        for (const line of lines) {
          try {
            const json: OllamaResponse = JSON.parse(line);
            if (json.message?.content) {
              accumulatedContent += json.message.content;
              onChunk(accumulatedContent);
            }
            if (json.done) {
              onComplete();
            }
          } catch (e) {
            console.error('Error parsing JSON:', e);
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      onComplete();
    } finally {
      setLoading(false);
    }
  }, [baseUrl]);

  return { models, loading, error, fetchModels, sendMessage };
};