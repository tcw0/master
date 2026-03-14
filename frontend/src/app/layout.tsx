import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "DDD Pipeline",
  description: "AI-Assisted Domain-Driven Design artifact generation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`min-h-screen bg-background text-foreground antialiased ${inter.variable} font-sans`}>
        <header className="border-b border-border bg-background">
          <div className="mx-auto flex h-14 max-w-5xl items-center px-6">
            <a href="/" className="flex items-center gap-2 font-semibold tracking-tight">
              <span className="text-lg">◇</span>
              <span>DDD Pipeline</span>
            </a>
          </div>
        </header>
        <TooltipProvider>
          <main className="mx-auto max-w-5xl px-6 py-8">
            {children}
          </main>
          <Toaster />
        </TooltipProvider>
      </body>
    </html>
  );
}
