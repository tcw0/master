"use client";

import { useParams, usePathname } from "next/navigation";
import Link from "next/link";
import { useEffect, useState } from "react";
import { getSession, type Session } from "@/lib/api";
import { CheckCircle2, Circle, Loader2, AlertCircle } from "lucide-react";

function StatusIcon({ status }: { status: string }) {
    switch (status) {
        case "completed":
            return <CheckCircle2 className="h-4 w-4 text-green-500" />;
        case "running":
            return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
        case "failed":
            return <AlertCircle className="h-4 w-4 text-destructive" />;
        default:
            return <Circle className="h-4 w-4 text-muted-foreground/50" />;
    }
}

export default function SessionLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const params = useParams<{ id: string }>();
    const pathname = usePathname();
    const [session, setSession] = useState<Session | null>(null);

    // Initial load
    useEffect(() => {
        getSession(params.id).then(setSession).catch(console.error);
    }, [params.id]);

    // Smart polling to keep the sidebar updated:
    // 1. Never poll if the tab is in the background (saves extreme compute if tab left open)
    // 2. Poll every 5s if a phase is currently running, otherwise every 30s to conserve the Vercel free tier
    const hasRunningPhase = session?.phases?.some(p => p.status === "running");

    useEffect(() => {
        let interval: NodeJS.Timeout;

        const checkSession = () => {
            if (document.visibilityState !== "visible") return;
            getSession(params.id).then(setSession).catch(console.error);
        };

        const pollFrequency = hasRunningPhase ? 5000 : 30000;
        interval = setInterval(checkSession, pollFrequency);

        return () => clearInterval(interval);
    }, [params.id, hasRunningPhase]);

    if (!session) {
        return (
            <div className="flex h-[50vh] items-center justify-center text-muted-foreground">
                Loading session environment...
            </div>
        );
    }

    const navLinks = [
        { href: `/sessions/${params.id}`, label: "Overview", icon: null },
        ...session.phases.map((p) => ({
            href: `/sessions/${params.id}/phases/${p.phase_id}`,
            label: `${p.phase_number}. ${p.phase_name}`,
            icon: <StatusIcon status={p.status} />,
        })),
    ];

    return (
        <div className="flex min-h-[calc(100vh-4rem)]">
            {/* Sidebar */}
            <aside className="w-64 shrink-0 border-r border-border pr-6 py-2">
                <div className="mb-6 space-y-1">
                    <Link href="/" className="text-xs text-muted-foreground hover:text-foreground mb-4 inline-block">
                        ← All Sessions
                    </Link>
                    <h2 className="font-semibold text-sm truncate" title={session.requirements_name}>
                        {session.requirements_name}
                    </h2>
                    <p className="text-xs text-muted-foreground font-mono truncate">
                        {session.id.split('-')[0]}
                    </p>
                </div>

                <nav className="space-y-1">
                    {navLinks.map((link) => {
                        const isActive = pathname === link.href;
                        return (
                            <Link
                                key={link.href}
                                href={link.href}
                                className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                                    isActive
                                        ? "bg-secondary text-secondary-foreground font-medium"
                                        : "hover:bg-muted/50 text-muted-foreground hover:text-foreground"
                                }`}
                            >
                                {link.icon && <span className="shrink-0">{link.icon}</span>}
                                <span>{link.label}</span>
                            </Link>
                        );
                    })}
                </nav>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 pl-8 py-2 min-w-0">
                {children}
            </main>
        </div>
    );
}
