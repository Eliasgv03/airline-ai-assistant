/**
 * API Client for Air India Assistant Backend
 *
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatRequest {
    session_id: string;
    message: string;
}

export interface ChatResponse {
    message: string;
    session_id: string;
    metadata?: Record<string, unknown>;
}

export interface StreamChunk {
    chunk?: string;
    done?: boolean;
    error?: string;
    session_id: string;
}

/**
 * Send a message to the chatbot and get a response
 */
export async function sendMessage(
    sessionId: string,
    message: string
): Promise<ChatResponse> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
            } as ChatRequest),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API error (${response.status}): ${errorText}`);
        }

        const data: ChatResponse = await response.json();
        return data;
    } catch (error) {
        console.error("API Error Details:", {
            message: error instanceof Error ? error.message : "Unknown error",
            error,
            url: `${API_BASE_URL}/api/chat/`
        });
        throw error
    }
}

/**
 * Send a message and stream the response in real-time
 *
 * @param sessionId - Unique session identifier
 * @param message - User's message
 * @param onChunk - Callback function called for each chunk received
 * @param onComplete - Callback function called when streaming is complete
 * @param onError - Callback function called if an error occurs
 */
export async function sendMessageStream(
    sessionId: string,
    message: string,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
): Promise<void> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
            } as ChatRequest),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API error (${response.status}): ${errorText}`);
        }

        // Read the stream
        const reader = response.body?.getReader();
        if (!reader) {
            throw new Error('Response body is not readable');
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                break;
            }

            // Decode the chunk
            buffer += decoder.decode(value, { stream: true });

            // Process complete SSE messages
            const lines = buffer.split('\n\n');
            buffer = lines.pop() || ''; // Keep incomplete message in buffer

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const dataStr = line.slice(6); // Remove 'data: ' prefix

                    try {
                        const data: StreamChunk = JSON.parse(dataStr);

                        if (data.error) {
                            onError(new Error(data.error));
                            return;
                        }

                        if (data.done) {
                            onComplete();
                            return;
                        }

                        if (data.chunk) {
                            onChunk(data.chunk);
                        }
                    } catch (parseError) {
                        console.error('Error parsing SSE data:', parseError, dataStr);
                    }
                }
            }
        }

        // If we exit the loop without getting 'done', call onComplete
        onComplete();

    } catch (error) {
        console.error("Streaming API Error:", {
            message: error instanceof Error ? error.message : "Unknown error",
            error,
            url: `${API_BASE_URL}/api/chat/stream`
        });
        onError(error instanceof Error ? error : new Error('Unknown streaming error'));
    }
}

/**
 * Generate a unique session ID
 */
export function generateSessionId(): string {
    // Use crypto.randomUUID if available, otherwise fallback
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID();
    }

    // Fallback for older browsers
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}
