"use client";

import { useState } from "react";
import { AlertCircle, CheckCircle2, Circle, Play, RotateCw, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { ArtifactViewer } from "@/components/artifacts/ArtifactViewer";
import { usePhase } from "@/hooks/use-phase";

interface PhasePageTemplateProps {
    sessionId: string;
    phaseNum: number;
    title: string;
    description: React.ReactNode;
}

function StatusBadge({ status }: { status: string }) {
    if (status === "completed") {
        return <Badge variant="default" className="bg-green-600 hover:bg-green-700"><CheckCircle2 className="w-3 h-3 mr-1" />Completed</Badge>;
    }
    if (status === "running") {
        return <Badge variant="secondary"><RotateCw className="w-3 h-3 mr-1 animate-spin" />Running</Badge>;
    }
    if (status === "failed") {
        return <Badge variant="destructive"><AlertCircle className="w-3 h-3 mr-1" />Failed</Badge>;
    }
    return <Badge variant="outline"><Circle className="w-3 h-3 mr-1" />Pending</Badge>;
}

export function PhasePageTemplate({
    sessionId,
    phaseNum,
    title,
    description,
}: PhasePageTemplateProps) {
    const { phase, artifact, loading, running, refining, isRunnable, handleRun, handleRefine } = usePhase(sessionId, phaseNum);
    const [instructions, setInstructions] = useState("");
    const [dialogOpen, setDialogOpen] = useState(false);

    const onRefineSubmit = async () => {
        if (instructions.trim()) {
            await handleRefine(instructions);
        } else {
            await handleRun();
        }
        setDialogOpen(false);
        setInstructions("");
    };

    if (loading || !phase) {
        return <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-1/3"></div>
            <div className="h-24 bg-muted/50 rounded w-full"></div>
        </div>;
    }

    return (
        <div className="space-y-6 max-w-5xl">
            {/* Header */}
            <div>
                <div className="flex items-center justify-between mb-4">
                    <h1 className="text-2xl font-bold tracking-tight">{phaseNum}. {title}</h1>
                    <div className="flex items-center gap-3">
                        <StatusBadge status={phase.status} />
                        {isRunnable && (
                            phase.status === "completed" ? (
                                <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                                    <DialogTrigger 
                                        render={
                                            <Button
                                                disabled={running || refining}
                                                size="sm"
                                                variant="secondary"
                                            />
                                        }
                                    >
                                        {(running || refining) ? (
                                            <><RotateCw className="w-4 h-4 mr-2 animate-spin" /> Running...</>
                                        ) : (
                                            <><RotateCw className="w-4 h-4 mr-2" /> Re-run Phase</>
                                        )}
                                    </DialogTrigger>
                                    <DialogContent>
                                        <DialogHeader>
                                            <DialogTitle>Re-run or Refine Artifact</DialogTitle>
                                            <DialogDescription>
                                                (Optional) Provide instructions to guide the LLM on exactly what to change.
                                            </DialogDescription>
                                        </DialogHeader>
                                        <Textarea
                                            placeholder="E.g., Add a 'User' entity..."
                                            value={instructions}
                                            onChange={(e) => setInstructions(e.target.value)}
                                            disabled={refining}
                                            className="min-h-[100px] resize-y"
                                        />
                                        <DialogFooter>
                                            <Button 
                                                variant="outline" 
                                                onClick={() => setDialogOpen(false)}
                                                disabled={refining}
                                            >
                                                Cancel
                                            </Button>
                                            <Button 
                                                onClick={onRefineSubmit}
                                                disabled={refining}
                                            >
                                                {refining ? (
                                                    <><RotateCw className="w-4 h-4 mr-2 animate-spin" /> Refining...</>
                                                ) : instructions.trim() ? (
                                                    <><Sparkles className="w-4 h-4 mr-2" /> Refine Artifact</>
                                                ) : (
                                                    <><RotateCw className="w-4 h-4 mr-2" /> Re-run Phase</>
                                                )}
                                            </Button>
                                        </DialogFooter>
                                    </DialogContent>
                                </Dialog>
                            ) : (
                                <Button
                                    onClick={handleRun}
                                    disabled={running || refining || phase.status === "running"}
                                    size="sm"
                                    variant="default"
                                >
                                    {running || phase.status === "running" ? (
                                        <><RotateCw className="w-4 h-4 mr-2 animate-spin" /> Running...</>
                                    ) : (
                                        <><Play className="w-4 h-4 mr-2" /> Start Phase</>
                                    )}
                                </Button>
                            )
                        )}
                    </div>
                </div>

                {/* Context / Description */}
                <p className="text-muted-foreground leading-relaxed">
                    {description}
                </p>
                
                {artifact && (
                    <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground border-l-2 border-border pl-3 py-1">
                        <span>Version {artifact.version}</span>
                        <span>·</span>
                        <span className="font-mono">{artifact.source}</span>
                        <span>·</span>
                        <span>Generated by {phase.source}</span>
                    </div>
                )}
            </div>

            <Separator />

            {/* Main Content Area */}
            <div className="min-h-[400px]">
                {phase.status === "running" || running ? (
                    <div className="flex flex-col items-center justify-center h-[400px] text-muted-foreground border rounded-lg bg-muted/10 border-dashed">
                        <RotateCw className="w-8 h-8 mb-4 animate-spin text-primary" />
                        <p>Generating {title.toLowerCase()}...</p>
                        <p className="text-xs mt-2">This usually takes 10-30 seconds depending on the model.</p>
                    </div>
                ) : phase.status === "failed" ? (
                    <div className="flex flex-col items-center justify-center h-[400px] text-destructive border-destructive/20 border rounded-lg bg-destructive/5">
                        <AlertCircle className="w-8 h-8 mb-4" />
                        <p>Phase execution failed.</p>
                        <p className="text-xs mt-2 text-muted-foreground">Check the logs or try running it again.</p>
                    </div>
                ) : artifact ? (
                    <ArtifactViewer phaseId={phase.phase_id} artifact={artifact.artifact} />
                ) : (
                    <div className="flex flex-col items-center justify-center h-[400px] text-muted-foreground border rounded-lg bg-muted/10 border-dashed">
                        <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mb-4">
                            <span className="text-xl font-medium">{phaseNum}</span>
                        </div>
                        <p>This phase has not been executed yet.</p>
                        {!isRunnable && (
                            <p className="text-xs mt-2 text-amber-500 max-w-sm text-center">
                                You must complete the previous phases before you can run this one.
                            </p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
