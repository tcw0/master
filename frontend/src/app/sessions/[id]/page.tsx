"use client";

import { useEffect, useState } from "react";
import { getSession, type Session } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Circle, Loader2, AlertCircle, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useParams, useRouter } from "next/navigation";
import { ScrollArea } from "@/components/ui/scroll-area";

function StatusIcon({ status }: { status: string }) {
    switch (status) {
        case "completed":
            return <CheckCircle2 className="h-5 w-5 text-green-500" />;
        case "running":
            return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
        case "failed":
            return <AlertCircle className="h-5 w-5 text-destructive" />;
        default:
            return <Circle className="h-5 w-5 text-muted-foreground/50" />;
    }
}

export default function SessionOverviewPage() {
    const params = useParams<{ id: string }>();
    const [session, setSession] = useState<Session | null>(null);
    const router = useRouter();

    useEffect(() => {
        getSession(params.id).then(setSession).catch(console.error);
    }, [params.id]);

    if (!session) {
        return <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-1/3"></div>
            <div className="h-40 bg-muted/50 rounded w-full"></div>
        </div>;
    }

    const completedCount = session.phases.filter(p => p.status === "completed").length;
    const progressPercent = Math.round((completedCount / session.phases.length) * 100);

    // Find the first non-completed phase to direct the user to
    const nextPhase = session.phases.find(p => p.status !== "completed") || session.phases[session.phases.length - 1];

    return (
        <div className="space-y-8 max-w-4xl">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold tracking-tight mb-2">Session Overview</h1>
                <p className="text-muted-foreground">
                    Review your overall progress and the initial requirements for this Domain-Driven Design session.
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {/* Stats Card */}
                <Card>
                    <CardHeader className="pb-4">
                        <CardTitle className="text-lg">Progress</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center gap-4 mb-4">
                            <div className="w-16 h-16 rounded-full border-4 border-muted flex items-center justify-center font-bold text-xl relative">
                                <span className="absolute inset-0 rounded-full border-4 border-primary" style={{ clipPath: `polygon(0 0, 100% 0, 100% ${progressPercent}%, 0 ${progressPercent}%)` }}></span>
                                {completedCount}/5
                            </div>
                            <div>
                                <p className="font-medium">{progressPercent}% Completed</p>
                                <p className="text-sm text-muted-foreground">All phases must be completed sequentially.</p>
                            </div>
                        </div>

                        <div className="space-y-2">
                            {session.phases.map(p => (
                                <div key={p.phase_id} className="flex items-center gap-3 text-sm">
                                    <StatusIcon status={p.status} />
                                    <span className={p.status === "completed" ? "text-foreground" : "text-muted-foreground"}>
                                        Phase {p.phase_number}: {p.phase_name}
                                    </span>
                                </div>
                            ))}
                        </div>

                        <div className="mt-6">
                            <Button 
                                className="w-full group" 
                                onClick={() => router.push(`/sessions/${session.id}/phases/${nextPhase.phase_id}`)}
                            >
                                {completedCount === 0 ? "Start Pipeline" : completedCount === 5 ? "Review Architecture" : `Continue to Phase ${nextPhase.phase_number}`}
                                <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* Meta Card */}
                <Card>
                    <CardHeader className="pb-4">
                        <CardTitle className="text-lg">Environment</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4 text-sm">
                        <div className="grid grid-cols-3 gap-1">
                            <span className="text-muted-foreground">Session ID</span>
                            <span className="col-span-2 font-mono text-xs break-all">{session.id}</span>
                        </div>
                        <div className="grid grid-cols-3 gap-1">
                            <span className="text-muted-foreground">Created</span>
                            <span className="col-span-2">{new Date(session.created_at).toLocaleString()}</span>
                        </div>
                        <div className="grid grid-cols-3 gap-1 items-center">
                            <span className="text-muted-foreground">Provider</span>
                            <div className="col-span-2">
                                <Badge variant="secondary" className="capitalize">{session.provider}</Badge>
                            </div>
                        </div>
                        <div className="grid grid-cols-3 gap-1 items-center">
                            <span className="text-muted-foreground">Model</span>
                            <div className="col-span-2">
                                <Badge variant="outline">{session.model}</Badge>
                            </div>
                        </div>
                        <div className="grid grid-cols-3 gap-1">
                            <span className="text-muted-foreground">Temperature</span>
                            <span className="col-span-2">{session.temperature}</span>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Input Context */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">Business Requirements Context</CardTitle>
                </CardHeader>
                <CardContent>
                    <ScrollArea className="h-64 rounded-md border bg-muted/20 p-4">
                        <div className="prose prose-sm dark:prose-invert max-w-none">
                            <p className="whitespace-pre-wrap font-serif text-muted-foreground/90">
                                {/* The backend doesn't currently return the raw requirements text in the Session model, 
                                    so we just show the name. If the backend is updated to return it, we can display it here. */}
                                {session.requirements_name}
                            </p>
                        </div>
                    </ScrollArea>
                    <p className="text-xs text-muted-foreground mt-3 italic">
                        This text serves as the grounding context for all LLM generations in this session.
                    </p>
                </CardContent>
            </Card>
        </div>
    );
}
