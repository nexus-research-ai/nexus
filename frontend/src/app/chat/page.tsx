'use client';

import { Suspense, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import ResearchAssistant from '@/components/ResearchAssistant';

function ChatWorkspace() {
  const router = useRouter();
  const params = useSearchParams();
  const backToWorkspace = useCallback(() => router.push('/'), [router]);
  return <main className="chat-page"><ResearchAssistant mode="page" initialConversationId={params.get('conversation')} onClose={backToWorkspace} /></main>;
}

export default function ChatPage() {
  return <Suspense fallback={<main className="chat-page-loading" role="status">Opening chat…</main>}><ChatWorkspace /></Suspense>;
}
