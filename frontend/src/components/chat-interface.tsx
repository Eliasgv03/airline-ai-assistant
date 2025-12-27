"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ChatMessage } from "./chat-message"
import { TypingIndicator } from "./typing-indicator"
import { FlightCard, type FlightData } from "./flight-card"
import { Send, Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { sendMessageStream, generateSessionId } from "@/lib/api"

interface Message {
    id: string
    content: string
    isUser: boolean
    timestamp: string
    flight?: FlightData
}

export function ChatInterface() {
    const [sessionId] = useState(() => generateSessionId())
    const [messages, setMessages] = useState<Message[]>([])
    const [inputValue, setInputValue] = useState("")
    const [isTyping, setIsTyping] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const { theme, setTheme } = useTheme()

    // Determine if we should show welcome screen (no messages yet)
    const showWelcomeScreen = messages.length === 0

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages, isTyping])

    const handleSendMessage = async () => {
        if (!inputValue.trim()) return

        const userMessage: Message = {
            id: Date.now().toString(),
            content: inputValue,
            isUser: true,
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        }

        setMessages((prev) => [...prev, userMessage])
        const currentInput = inputValue
        setInputValue("")
        setIsTyping(true)

        // Create placeholder message for streaming response
        const assistantMessageId = (Date.now() + 1).toString()
        const assistantMessage: Message = {
            id: assistantMessageId,
            content: "",
            isUser: false,
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        }
        setMessages((prev) => [...prev, assistantMessage])

        try {
            // Use streaming API
            await sendMessageStream(
                sessionId,
                currentInput,
                // onChunk: append each chunk to the message
                (chunk: string) => {
                    setMessages((prev) =>
                        prev.map((msg) =>
                            msg.id === assistantMessageId
                                ? { ...msg, content: msg.content + chunk }
                                : msg
                        )
                    )
                },
                // onComplete: stop typing indicator
                () => {
                    setIsTyping(false)
                },
                // onError: handle errors
                (error: Error) => {
                    console.error("Error streaming message:", error)
                    setIsTyping(false)

                    // Update message with error
                    setMessages((prev) =>
                        prev.map((msg) =>
                            msg.id === assistantMessageId
                                ? { ...msg, content: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment." }
                                : msg
                        )
                    )
                }
            )
        } catch (err) {
            console.error("Error sending message:", err)
            setIsTyping(false)

            // Update message with error
            setMessages((prev) =>
                prev.map((msg) =>
                    msg.id === assistantMessageId
                        ? { ...msg, content: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment." }
                        : msg
                )
            )
        }
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            handleSendMessage()
        }
    }

    return (
        <div className="flex flex-col h-screen bg-background">
            {/* Header */}
            <header className="border-b border-border bg-card shadow-sm sticky top-0 z-10">
                <div className="flex items-center justify-between px-4 md:px-6 py-4">
                    <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-air-india-orange flex items-center justify-center">
                            <svg viewBox="0 0 24 24" className="h-6 w-6 text-white" fill="currentColor">
                                <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z" />
                            </svg>
                        </div>
                        <div>
                            <h1 className="text-lg md:text-xl font-bold text-foreground">Air India Assistant</h1>
                            <p className="text-xs text-muted-foreground">Always here to help</p>
                        </div>
                    </div>

                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                        className="shrink-0"
                    >
                        <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
                        <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
                        <span className="sr-only">Toggle theme</span>
                    </Button>
                </div>
            </header>

            {showWelcomeScreen ? (
                // Welcome Screen - Centered
                <div className="flex-1 flex flex-col items-center justify-center px-4 md:px-6">
                    <div className="max-w-2xl w-full text-center space-y-6">
                        {/* Air India Logo */}
                        <div className="flex justify-center">
                            <div className="h-20 w-20 rounded-full bg-air-india-orange flex items-center justify-center shadow-lg">
                                <svg viewBox="0 0 24 24" className="h-12 w-12 text-white" fill="currentColor">
                                    <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z" />
                                </svg>
                            </div>
                        </div>

                        {/* Welcome Message */}
                        <div className="space-y-3">
                            <h2 className="text-3xl md:text-4xl font-bold text-foreground">Welcome to Air India</h2>
                            <p className="text-lg md:text-xl text-muted-foreground">
                                Your virtual travel assistant is here to help
                            </p>
                        </div>

                        {/* Feature Cards */}
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8">
                            <div className="bg-card border border-border rounded-lg p-4 text-center hover:border-air-india-orange transition-colors">
                                <div className="text-2xl mb-2">✈️</div>
                                <p className="text-sm font-medium text-foreground">Flight Search</p>
                                <p className="text-xs text-muted-foreground mt-1">Find the best flights</p>
                            </div>
                            <div className="bg-card border border-border rounded-lg p-4 text-center hover:border-air-india-orange transition-colors">
                                <div className="text-2xl mb-2">🧳</div>
                                <p className="text-sm font-medium text-foreground">Baggage Info</p>
                                <p className="text-xs text-muted-foreground mt-1">Policies & allowances</p>
                            </div>
                            <div className="bg-card border border-border rounded-lg p-4 text-center hover:border-air-india-orange transition-colors">
                                <div className="text-2xl mb-2">💬</div>
                                <p className="text-sm font-medium text-foreground">24/7 Support</p>
                                <p className="text-xs text-muted-foreground mt-1">Always here to help</p>
                            </div>
                        </div>

                        {/* Input - Centered on Welcome Screen */}
                        <div className="max-w-2xl w-full mt-8">
                            <div className="flex gap-2 md:gap-3">
                                <Input
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Ask me anything about your travel..."
                                    className="flex-1 text-sm md:text-base h-12"
                                />
                                <Button
                                    onClick={handleSendMessage}
                                    size="icon"
                                    className="shrink-0 h-12 w-12 bg-air-india-orange hover:bg-air-india-orange/90 text-white"
                                    disabled={!inputValue.trim() || isTyping}
                                >
                                    <Send className="h-5 w-5" />
                                    <span className="sr-only">Send message</span>
                                </Button>
                            </div>
                            <p className="text-xs text-muted-foreground mt-3 text-center">
                                Try asking: &quot;Find flights from Delhi to Mumbai&quot; or &quot;What&apos;s the baggage allowance?&quot;
                            </p>
                        </div>
                    </div>
                </div>
            ) : (
                // Chat Messages - Normal Layout
                <>
                    <div className="flex-1 overflow-y-auto px-4 md:px-6 py-6">
                        <div className="max-w-4xl mx-auto">
                            {messages.map((message) => (
                                <div key={message.id}>
                                    {message.flight ? (
                                        <div className="mb-4 flex justify-start">
                                            <div className="max-w-[90%] md:max-w-[80%]">
                                                <FlightCard flight={message.flight} />
                                            </div>
                                        </div>
                                    ) : (
                                        <ChatMessage message={message.content} isUser={message.isUser} timestamp={message.timestamp} />
                                    )}
                                </div>
                            ))}

                            {isTyping && <TypingIndicator />}
                            <div ref={messagesEndRef} />
                        </div>
                    </div>

                    {/* Input - Bottom Position During Chat */}
                    <div className="border-t border-border bg-card shadow-lg sticky bottom-0">
                        <div className="max-w-4xl mx-auto px-4 md:px-6 py-4">
                            <div className="flex gap-2 md:gap-3">
                                <Input
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Type your message..."
                                    className="flex-1 text-sm md:text-base"
                                    disabled={isTyping}
                                />
                                <Button
                                    onClick={handleSendMessage}
                                    size="icon"
                                    className="shrink-0 bg-air-india-orange hover:bg-air-india-orange/90 text-white"
                                    disabled={!inputValue.trim() || isTyping}
                                >
                                    <Send className="h-4 w-4 md:h-5 md:w-5" />
                                    <span className="sr-only">Send message</span>
                                </Button>
                            </div>
                            <p className="text-xs text-muted-foreground mt-2 text-center">
                                Press Enter to send • Air India Virtual Assistant
                            </p>
                        </div>
                    </div>
                </>
            )}
        </div>
    )
}
