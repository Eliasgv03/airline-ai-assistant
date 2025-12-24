"use client"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Plane } from "lucide-react"

export function TypingIndicator() {
    return (
        <div className="flex gap-3 mb-4 items-start animate-in fade-in slide-in-from-bottom-2 duration-300">
            <Avatar className="h-8 w-8 shrink-0 bg-air-india-orange">
                <AvatarFallback className="text-white">
                    <Plane className="h-4 w-4" />
                </AvatarFallback>
            </Avatar>

            <div className="bg-card border border-border rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:-0.3s]" />
                    <div className="w-2 h-2 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:-0.15s]" />
                    <div className="w-2 h-2 rounded-full bg-muted-foreground/60 animate-bounce" />
                </div>
            </div>
        </div>
    )
}
