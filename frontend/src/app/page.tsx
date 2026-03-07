"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Loader2, FileText, Trash2, GitPullRequest } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";

import { createSession, listSessions, deleteSession, type Session } from "@/lib/api";
import { useEffect } from "react";

export default function HomePage() {
  const router = useRouter();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(false);

  // Form state
  const [requirementsText, setRequirementsText] = useState("");
  const [requirementsName, setRequirementsName] = useState("requirements");
  const [provider, setProvider] = useState("openrouter");
  const [model, setModel] = useState("openai/gpt-4.1-mini");
  const [temperature, setTemperature] = useState(0.3);

  useEffect(() => {
    loadSessions();
  }, []);

  async function loadSessions() {
    try {
      const data = await listSessions();
      setSessions(data.sessions);
    } catch (e) {
      toast.error("Failed to load sessions");
    }
  }

  async function handleCreate() {
    if (!requirementsText.trim()) {
      toast.error("Please enter requirements text");
      return;
    }
    setLoading(true);
    try {
      const session = await createSession({
        requirements_text: requirementsText,
        requirements_name: requirementsName,
        provider,
        model,
        temperature,
      });
      toast.success("Session created");
      router.push(`/sessions/${session.id}`);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to create session");
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteSession(id);
      toast.success("Session deleted");
      loadSessions();
    } catch (e) {
      toast.error("Failed to delete session");
    }
  }

  function getCompletedCount(session: Session): number {
    return session.phases.filter((p) => p.status === "completed").length;
  }

  return (
    <div className="space-y-8">
      {/* Create Session */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GitPullRequest className="h-5 w-5" />
            New Pipeline Session
          </CardTitle>
          <CardDescription>
            Paste your requirements and configure the LLM to start generating DDD artifacts.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="requirements">Requirements</Label>
              <Textarea
                id="requirements"
                placeholder="Paste your requirements document here..."
                className="min-h-[160px] font-mono text-sm"
                value={requirementsText}
                onChange={(e) => setRequirementsText(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="name">Project Name</Label>
              <Input
                id="name"
                value={requirementsName}
                onChange={(e) => setRequirementsName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="provider">Provider</Label>
              <Select value={provider} onValueChange={(v) => v && setProvider(v)}>
                <SelectTrigger id="provider">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="openrouter">OpenRouter</SelectItem>
                  <SelectItem value="ollama">Ollama (local)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="model">Model</Label>
              <Input
                id="model"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                placeholder="e.g. openai/gpt-4.1-mini"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="temperature">Temperature</Label>
              <Input
                id="temperature"
                type="number"
                min={0}
                max={1}
                step={0.1}
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
              />
            </div>
          </div>
          <Button onClick={handleCreate} disabled={loading} className="w-full">
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {loading ? "Creating Session..." : "Create Session & Start Pipeline"}
          </Button>
        </CardContent>
      </Card>

      {/* Previous Sessions */}
      {sessions.length > 0 && (
        <>
          <Separator />
          <div className="space-y-3">
            <h2 className="text-lg font-semibold">Previous Sessions</h2>
            <div className="grid gap-3">
              {sessions.map((s) => (
                <Card
                  key={s.id}
                  className="cursor-pointer transition-colors hover:bg-muted/50"
                  onClick={() => router.push(`/sessions/${s.id}`)}
                >
                  <CardContent className="flex items-center justify-between py-4">
                    <div className="flex items-start gap-3">
                      <div className="mt-1 bg-primary/10 p-2 rounded-md">
                        <FileText className="h-4 w-4 text-primary" />
                      </div>
                      <div className="space-y-1">
                        <p className="font-medium leading-none">{s.requirements_name}</p>
                        <p className="text-sm text-muted-foreground pt-1">
                          {s.provider}/{s.model} · {getCompletedCount(s)}/5 phases ·{" "}
                          <span className="font-mono text-xs">{s.id}</span>
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-muted-foreground hover:text-destructive"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(s.id);
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                      <span className="sr-only">Delete</span>
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
