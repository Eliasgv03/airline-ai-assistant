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
    metadata?: Record<string, any>;
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
