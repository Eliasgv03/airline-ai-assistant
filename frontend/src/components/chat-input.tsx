"use client"

import type React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send } from "lucide-react"

interface ChatInputProps {
    value: string
    onChange: (value: string) => void
    onSend: () => void
    disabled?: boolean
    placeholder?: string
    size?: "default" | "large"
    helperText?: string
}

export function ChatInput({
    value,
    onChange,
    onSend,
    disabled = false,
    placeholder = "Type your message...",
    size = "default",
    helperText,
}: ChatInputProps) {
    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            if (value.trim() && !disabled) {
                onSend()
            }
        }
    }

    const isLarge = size === "large"

    return (
        <div className="w-full">
            <div className="flex gap-2 md:gap-3">
                <Input
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={placeholder}
                    className={`flex-1 text-sm md:text-base ${isLarge ? "h-12" : ""}`}
                />
                <Button
                    onClick={onSend}
                    size="icon"
                    className={`shrink-0 bg-air-india-orange hover:bg-air-india-orange/90 text-white ${isLarge ? "h-12 w-12" : ""}`}
                    disabled={!value.trim() || disabled}
                >
                    <Send className={isLarge ? "h-5 w-5" : "h-4 w-4 md:h-5 md:w-5"} />
                    <span className="sr-only">Send message</span>
                </Button>
            </div>
            {helperText && (
                <p className="text-xs text-muted-foreground mt-2 md:mt-3 text-center">
                    {helperText}
                </p>
            )}
        </div>
    )
}
