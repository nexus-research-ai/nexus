'use client';

import { useEffect, useRef, useState, type FormEvent } from 'react';
import Link from 'next/link';
import { ArrowUp, BookOpen, ChevronLeft, Clock3, ExternalLink, Maximize2, MessageSquare, Plus, Search, Square, Trash2, X } from 'lucide-react';
import { ApiError, api, type ChatCitation, type ChatMessage } from '@/lib/api';
import { safeOrigin } from '@/lib/editor';

type Message = ChatMessage & { id: string; citations?: ChatCitation[] };
type Conversation = { id: string; title: string; updatedAt: string; messages: Message[] };
const historyKey = 'nexus.recent-chats.v1';
const suggestions = [
  { title: 'Develop a research idea', prompt: 'Help me turn a research idea into a clear, testable question.' },
  { title: 'Plan a literature review', prompt: 'Help me make a plan for a literature review. Start by asking about my topic.' },
  { title: 'Prepare a grant outline', prompt: 'Help me outline a research grant proposal. What information do you need first?' },
];

function readConversations(): Conversation[] {
  try {
    const raw: unknown = JSON.parse(localStorage.getItem(historyKey) || '[]');
    if (!Array.isArray(raw)) return [];
    return raw.filter((item): item is Conversation => Boolean(item && typeof item.id === 'string' && typeof item.title === 'string' && typeof item.updatedAt === 'string' && Array.isArray(item.messages) && item.messages.every((message: Message) => message && typeof message.id === 'string' && typeof message.content === 'string' && (message.role === 'user' || message.role === 'assistant'))))
      .slice(0, 30).map(item => ({ ...item, messages: item.messages.slice(-80) }));
  } catch { return []; }
}

export default function ResearchAssistant({ onClose, initialPrompt, mode = 'panel', initialConversationId }: { onClose: () => void; initialPrompt?: string; mode?: 'panel' | 'page'; initialConversationId?: string | null }) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const [activeId, setActiveId] = useState<string | null>(initialConversationId || null);
  const [draft, setDraft] = useState(initialPrompt || '');
  const [historySearch, setHistorySearch] = useState('');
  const [historyOpen, setHistoryOpen] = useState(false);
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [errorConversationId, setErrorConversationId] = useState<string | null>(null);
  const [storageError, setStorageError] = useState('');
  const closeRef = useRef(onClose);
  useEffect(() => { closeRef.current = onClose; }, [onClose]);
  const dialogRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const requestRef = useRef<AbortController | null>(null);
  const active = conversations.find(item => item.id === activeId);
  const messages = active?.messages ?? [];
  const recent = [...conversations].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt)).filter(item => item.title.toLowerCase().includes(historySearch.trim().toLowerCase()));

  useEffect(() => { setConversations(readConversations()); setHistoryLoaded(true); }, []);

  useEffect(() => {
    if (!historyLoaded) return;
    try { localStorage.setItem(historyKey, JSON.stringify(conversations)); }
    catch { setStorageError('Browser storage is unavailable. Chats will only last until you close this panel.'); }
  }, [conversations, historyLoaded]);

  useEffect(() => {
    if (mode === 'page') { inputRef.current?.focus(); return () => requestRef.current?.abort(); }
    const previousFocus = document.activeElement as HTMLElement | null;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    inputRef.current?.focus();
    const keydown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { event.preventDefault(); closeRef.current(); return; }
      if (event.key !== 'Tab') return;
      const elements = [...(dialogRef.current?.querySelectorAll<HTMLElement>('button:not(:disabled), input, textarea, a[href]') ?? [])].filter(element => element.getClientRects().length > 0);
      const first = elements[0];
      const last = elements[elements.length - 1];
      if (event.shiftKey && (document.activeElement === first || !dialogRef.current?.contains(document.activeElement))) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && (document.activeElement === last || !dialogRef.current?.contains(document.activeElement))) { event.preventDefault(); first?.focus(); }
    };
    document.addEventListener('keydown', keydown);
    return () => { document.body.style.overflow = previousOverflow; document.removeEventListener('keydown', keydown); requestRef.current?.abort(); previousFocus?.focus(); };
  }, [mode]);

  useEffect(() => { if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight; }, [activeId, messages.length, pendingId]);

  const newChat = () => { setActiveId(null); setDraft(''); setError(''); setHistoryOpen(false); inputRef.current?.focus(); };
  const openChat = (id: string) => { setActiveId(id); setDraft(''); setError(''); setHistoryOpen(false); inputRef.current?.focus(); };

  const send = async (text: string, retry = false) => {
    if (!text.trim() || pendingId || !historyLoaded) return;
    const id = activeId ?? crypto.randomUUID();
    const controller = new AbortController();
    requestRef.current = controller;
    const previous = retry ? messages.slice(0, -1) : messages;
    const outgoing: Message = { id: crypto.randomUUID(), role: 'user', content: text.trim() };
    const nextMessages = retry ? messages : [...messages, outgoing];
    const now = new Date().toISOString();
    setConversations(current => {
      const existing = current.find(item => item.id === id);
      const updated: Conversation = { id, title: existing?.title ?? text.trim().slice(0, 65), updatedAt: now, messages: nextMessages.slice(-80) };
      return [updated, ...current.filter(item => item.id !== id)].slice(0, 30);
    });
    setActiveId(id);
    setDraft('');
    setError('');
    setPendingId(id);
    try {
      const result = await api.chat({ message: text.trim(), history: previous.slice(-20).map(({ role, content }) => ({ role, content: content.slice(0, 8000) })) }, controller.signal);
      if (controller.signal.aborted) return;
      if (!result.response?.trim()) throw new Error('The service returned an empty reply. Please try again.');
      const reply: Message = { id: crypto.randomUUID(), role: 'assistant', content: result.response, citations: result.citations };
      setConversations(current => current.map(item => item.id === id ? { ...item, updatedAt: new Date().toISOString(), messages: [...item.messages, reply].slice(-80) } : item));
    } catch (err) {
      if (controller.signal.aborted) return;
      setErrorConversationId(id);
      setError(err instanceof ApiError && [404, 503].includes(err.status) ? 'Chat is currently unavailable. Your message is saved; try again when the service is connected.' : err instanceof ApiError && err.status === 502 ? 'The reply service couldn’t respond. Your message is saved. Please try again.' : err instanceof Error ? err.message : 'The message couldn’t be sent. Please try again.');
    } finally { if (!controller.signal.aborted) { setPendingId(null); requestRef.current = null; } }
  };

  const submit = (event: FormEvent) => { event.preventDefault(); void send(draft); };
  const stop = () => { requestRef.current?.abort(); requestRef.current = null; setPendingId(null); };

  return <div className={`research-chat-backdrop research-chat-${mode}-backdrop`} onClick={mode === 'panel' ? onClose : undefined}>
    <div ref={dialogRef} className={`research-chat research-chat-${mode} ${historyOpen ? 'chat-history-open' : ''}`} role={mode === 'panel' ? 'dialog' : undefined} aria-modal={mode === 'panel' ? true : undefined} aria-labelledby="research-chat-title" onClick={event => event.stopPropagation()}>
      <aside className="chat-history" aria-label="Recent chats">
        <div className="chat-history-top"><span><MessageSquare size={18} /> Nexus AI</span><button className="icon-button chat-history-close" aria-label="Close recent chats" onClick={() => setHistoryOpen(false)}><ChevronLeft size={16} /></button></div>
        <button className="kg-button chat-new" onClick={newChat}><Plus size={16} />New chat</button>
        <h2>Recent chats</h2>
        {conversations.length > 0 && <label className="chat-history-search"><Search size={14} /><input aria-label="Search recent chats" placeholder="Search chats" value={historySearch} onChange={event => setHistorySearch(event.target.value)} /></label>}
        <div className="chat-history-items">{!recent.length && <p className="chat-history-empty">{historySearch ? 'No chats match your search.' : 'Your conversations will appear here.'}</p>}
          {recent.map(item => <div key={item.id} className={`chat-history-item ${activeId === item.id ? 'active' : ''}`}><button onClick={() => openChat(item.id)} aria-pressed={activeId === item.id}><span>{item.title}</span><small>{new Date(item.updatedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</small></button><button aria-label={`Delete chat: ${item.title}`} title="Delete chat" onClick={() => { setConversations(current => current.filter(chat => chat.id !== item.id)); if (activeId === item.id) newChat(); }} disabled={pendingId === item.id}><Trash2 size={14} /></button></div>)}
        </div>
        {mode === 'page' && <Link className="chat-workspace-link" href="/">Back to workspace</Link>}
        <p className="chat-history-note">Recent chats are saved in this browser.</p>
      </aside>
      <section className="chat-main">
        <header className="chat-header"><div><h2 id="research-chat-title">{mode === 'panel' ? 'Nexus AI' : active?.title || 'New chat'}</h2><span>{mode === 'panel' ? active?.title || 'Your research assistant' : 'Nexus AI · Research assistant'}</span></div><div><button className="icon-button chat-show-history" aria-label="Show recent chats" title="Recent chats" onClick={() => setHistoryOpen(true)}><Clock3 size={18} /></button><button className="icon-button" aria-label="Start a new chat" title="New chat" onClick={newChat}><Plus size={18} /></button>{mode === 'panel' && <Link className="icon-button" aria-label="Open chat page" title="Open chat page" href={activeId ? `/chat?conversation=${encodeURIComponent(activeId)}` : '/chat'}><Maximize2 size={17} /></Link>}<button className="icon-button" aria-label={mode === 'panel' ? 'Close research assistant' : 'Back to workspace'} title={mode === 'panel' ? 'Close' : 'Back to workspace'} onClick={onClose}>{mode === 'panel' ? <X size={18} /> : <ChevronLeft size={18} />}</button></div></header>
        <div className="chat-conversation" ref={scrollRef} role="log" aria-label="Conversation" aria-live="polite">
          {!messages.length && <div className="chat-welcome"><div className="chat-welcome-icon"><BookOpen size={26} /></div><h3>What are you working on?</h3><p>Start with a question or choose a starting point below.</p><div className="chat-suggestions">{suggestions.map(item => <button key={item.title} onClick={() => { setDraft(item.prompt); inputRef.current?.focus(); }}><span>{item.title}</span><Plus size={15} /></button>)}</div></div>}
          {messages.map(message => <article key={message.id} className={`chat-message ${message.role}`}><span className="chat-message-role">{message.role === 'user' ? 'You' : 'Nexus'}</span><div className="chat-message-content">{message.content}</div>{Array.isArray(message.citations) && message.citations.length > 0 && <div className="chat-sources"><span>Sources</span>{message.citations.map((citation, index) => safeOrigin(citation.origin) && <a key={`${citation.source_id}-${index}`} href={safeOrigin(citation.origin)} target="_blank" rel="noopener noreferrer">{citation.title}<ExternalLink size={12} /></a>)}</div>}</article>)}
          {pendingId && pendingId === activeId && <div className="chat-pending" role="status"><span className="spinner" />Preparing a reply…</div>}
        </div>
        <div className="chat-composer-area">
          {storageError && <p className="chat-error" role="status">{storageError}</p>}
          {error && errorConversationId === activeId && <p className="chat-error" role="alert">{error}</p>}
          {!pendingId && messages.at(-1)?.role === 'user' && <button className="chat-retry" onClick={() => void send(messages.at(-1)!.content, true)}>Retry last message</button>}
          <form className="chat-composer" onSubmit={submit}><label htmlFor="research-chat-message" className="sr-only">Message Nexus</label><textarea id="research-chat-message" ref={inputRef} rows={2} maxLength={4000} placeholder="Ask a research question…" value={draft} onChange={event => setDraft(event.target.value)} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); if (!pendingId) void send(draft); } }} /><div><span>Enter to send · Shift + Enter for a new line</span>{pendingId ? <button type="button" aria-label="Stop reply" onClick={stop}><Square size={15} /></button> : <button type="submit" aria-label="Send message" disabled={!draft.trim()}><ArrowUp size={18} /></button>}</div></form>
          <p className="chat-disclaimer">Review important details and check original sources.</p>
        </div>
      </section>
    </div>
  </div>;
}
