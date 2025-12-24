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

interface Message {
    id: string
    content: string
    isUser: boolean
    timestamp: string
    flight?: FlightData
}

export function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "1",
            content:
                "Welcome to Air India! I'm your virtual assistant. How can I help you today? You can ask me about flights, bookings, or any travel-related queries.",
            isUser: false,
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
    ])
    const [inputValue, setInputValue] = useState("")
    const [isTyping, setIsTyping] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const { theme, setTheme } = useTheme()

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
        setInputValue("")
        setIsTyping(true)

        // Simulate assistant response
        setTimeout(() => {
            setIsTyping(false)

            // Check if user is asking about flights
            const isFlightQuery =
                inputValue.toLowerCase().includes("flight") ||
                inputValue.toLowerCase().includes("delhi") ||
                inputValue.toLowerCase().includes("mumbai")

            if (isFlightQuery) {
                const assistantMessage: Message = {
                    id: (Date.now() + 1).toString(),
                    content: "I found some available flights for you. Here are the best options:",
                    isUser: false,
                    timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                }

                const flightMessage: Message = {
                    id: (Date.now() + 2).toString(),
                    content: "",
                    isUser: false,
                    timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                    flight: {
                        flightNumber: "AI 860",
                        from: "Indira Gandhi International Airport",
                        to: "Chhatrapati Shivaji Maharaj International Airport",
                        fromCode: "DEL",
                        toCode: "BOM",
                        departureTime: "14:30",
                        arrivalTime: "16:45",
                        date: "December 28, 2025",
                        duration: "2h 15m",
                        price: "₹8,450",
                        aircraft: "Boeing 787 Dreamliner",
                    },
                }

                setMessages((prev) => [...prev, assistantMessage, flightMessage])
            } else {
                const assistantMessage: Message = {
                    id: (Date.now() + 1).toString(),
                    content:
                        "I understand your query. I can help you with flight bookings, check-in, baggage information, flight status, and more. Would you like to search for a flight?",
                    isUser: false,
                    timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                }

                setMessages((prev) => [...prev, assistantMessage])
            }
        }, 1500)
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

            {/* Messages */}
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

            {/* Input */}
            <div className="border-t border-border bg-card shadow-lg sticky bottom-0">
                <div className="max-w-4xl mx-auto px-4 md:px-6 py-4">
                    <div className="flex gap-2 md:gap-3">
                        <Input
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Type your message..."
                            className="flex-1 text-sm md:text-base"
                        />
                        <Button
                            onClick={handleSendMessage}
                            size="icon"
                            className="shrink-0 bg-air-india-orange hover:bg-air-india-orange/90 text-white"
                            disabled={!inputValue.trim()}
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
        </div>
    )
}
