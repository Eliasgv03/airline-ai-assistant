"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Plane, Clock, Calendar } from "lucide-react"
import { cn } from "@/lib/utils"

export interface FlightData {
    flightNumber: string
    from: string
    to: string
    fromCode: string
    toCode: string
    departureTime: string
    arrivalTime: string
    date: string
    duration: string
    price: string
    aircraft?: string
}

interface FlightCardProps {
    flight: FlightData
    className?: string
}

export function FlightCard({ flight, className }: FlightCardProps) {
    return (
        <Card className={cn("overflow-hidden border-border shadow-sm hover:shadow-md transition-shadow", className)}>
            <CardContent className="p-4 md:p-6">
                {/* Flight number and aircraft */}
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-full bg-air-india-orange flex items-center justify-center">
                            <Plane className="h-4 w-4 text-white" />
                        </div>
                        <div>
                            <p className="font-semibold text-sm md:text-base">Air India {flight.flightNumber}</p>
                            {flight.aircraft && <p className="text-xs text-muted-foreground">{flight.aircraft}</p>}
                        </div>
                    </div>
                    <div className="text-right">
                        <p className="text-lg md:text-xl font-bold text-air-india-orange">{flight.price}</p>
                    </div>
                </div>

                {/* Flight route */}
                <div className="flex items-center justify-between mb-4">
                    <div className="flex-1">
                        <p className="text-2xl md:text-3xl font-bold">{flight.departureTime}</p>
                        <p className="text-sm font-medium">{flight.fromCode}</p>
                        <p className="text-xs text-muted-foreground line-clamp-1">{flight.from}</p>
                    </div>

                    <div className="flex-1 flex flex-col items-center px-2 md:px-4">
                        <p className="text-xs text-muted-foreground mb-1">{flight.duration}</p>
                        <div className="w-full h-px bg-border relative">
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-2 w-2 rounded-full bg-air-india-orange" />
                        </div>
                        <Plane className="h-4 w-4 text-air-india-orange mt-1 rotate-90" />
                    </div>

                    <div className="flex-1 text-right">
                        <p className="text-2xl md:text-3xl font-bold">{flight.arrivalTime}</p>
                        <p className="text-sm font-medium">{flight.toCode}</p>
                        <p className="text-xs text-muted-foreground line-clamp-1">{flight.to}</p>
                    </div>
                </div>

                {/* Date and duration */}
                <div className="flex items-center gap-4 mb-4 text-xs md:text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span>{flight.date}</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        <span>{flight.duration}</span>
                    </div>
                </div>

                {/* Action button */}
                <Button className="w-full bg-air-india-orange hover:bg-air-india-orange/90 text-white">Select Flight</Button>
            </CardContent>
        </Card>
    )
}
