"use client"

import { cn } from "@/lib/utils"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Plane, User } from "lucide-react"

interface ChatMessageProps {
    message: string
    isUser: boolean
    timestamp?: string
}

export function ChatMessage({ message, isUser, timestamp }: ChatMessageProps) {
    return (
        <div
            className={cn(
                "flex gap-3 mb-4 items-start animate-in fade-in slide-in-from-bottom-2 duration-300",
                isUser ? "flex-row-reverse" : "flex-row",
            )}
        >
            <Avatar className={cn("h-8 w-8 shrink-0", isUser ? "bg-air-india-blue" : "bg-air-india-orange")}>
                <AvatarFallback className="text-white">
                    {isUser ? <User className="h-4 w-4" /> : <Plane className="h-4 w-4" />}
                </AvatarFallback>
            </Avatar>

            <div className={cn("flex flex-col gap-1 max-w-[80%] md:max-w-[70%]", isUser ? "items-end" : "items-start")}>
                <div
                    className={cn(
                        "rounded-2xl px-4 py-3 text-sm md:text-base shadow-sm",
                        isUser
                            ? "bg-air-india-blue text-white rounded-tr-sm"
                            : "bg-card border border-border text-card-foreground rounded-tl-sm",
                    )}
                >
                    <p className="leading-relaxed">{message}</p>
                </div>

                {timestamp && <span className="text-xs text-muted-foreground px-1">{timestamp}</span>}
            </div>
        </div>
    )
}
