'use client';

import { useState } from 'react';
import { Bookmark, Check, MessageSquare, Plus } from 'lucide-react';
import { currentDemoProfileId, demoFeed, projectOwners } from '@/lib/demo';
import { useLocalState } from '@/lib/useLocalState';

const portraits: Record<string, string> = { JL: 'jon_lee', EC: 'emily_chen', AM: 'aria_malik', DM: 'david_miller', SR: 'sarah_rao' };
const isOwnPost = (initials: string) => projectOwners.some(owner => owner.initials === initials && owner.ownerId === currentDemoProfileId);

export default function DemoCommunityFeed({ sortOrder = "relevant" }: { sortOrder?: "relevant" | "recent" }) {
  const [following, setFollowing] = useLocalState<string[]>('nexus.demo.followed-projects', []);
  const [saved, setSaved] = useLocalState<string[]>('nexus.demo.saved-projects', []);
  const [comments, setComments] = useLocalState<Record<string, { author: string; text: string }[]>>('nexus.demo.feed-comments', {});
  const [expanded, setExpanded] = useState<string | null>(null);
  const [draft, setDraft] = useState('');
  const toggle = (values: string[], id: string) => values.includes(id) ? values.filter(value => value !== id) : [...values, id];
  const posts = sortOrder === "recent" ? demoFeed : [...demoFeed].sort((a, b) => Number(isOwnPost(b.initials)) - Number(isOwnPost(a.initials)));
  return <>{posts.map(post => <article key={post.id} className="feed-card clean-card project-post demo-community-post">
    <header className="feed-card-header"><span className="avatar"><img src={`/avatars/${portraits[post.initials]}.jpg`} alt={post.author} /></span><div><strong>{post.author}</strong><span>{post.role} · {post.time}</span></div><span className="demo-content-label">Demo</span></header>
    <div className="project-post-copy"><span className="demo-post-stage">{post.stage}</span><h2>{post.title}</h2><p>{post.body}</p><div className="demo-feed-tags">{post.offer.map(tag => <span className="tag tag-offer" key={tag}>{tag}</span>)}{post.need.map(tag => <span className="tag tag-need" key={tag}>Needs: {tag}</span>)}</div></div>
    <footer className="feed-card-actions">{isOwnPost(post.initials) ? <span className="demo-own-project">Your project</span> : <button aria-pressed={following.includes(post.id)} onClick={() => setFollowing(previous => toggle(previous, post.id))}>{following.includes(post.id) ? <Check size={16} /> : <Plus size={16} />}{following.includes(post.id) ? 'Following' : 'Follow project'}</button>}<button aria-expanded={expanded === post.id} onClick={() => { setExpanded(expanded === post.id ? null : post.id); setDraft(''); }}><MessageSquare size={16} />Comment ({post.comments.length + (comments[post.id]?.length ?? 0)})</button><button aria-pressed={saved.includes(post.id)} onClick={() => setSaved(previous => toggle(previous, post.id))}><Bookmark size={16} />{saved.includes(post.id) ? 'Saved' : 'Save'}</button></footer>
    {expanded === post.id && <div className="comment-thread">{[...post.comments, ...(comments[post.id] ?? [])].map((comment, index) => <div className="comment-item" key={index}><p><strong>{comment.author}</strong>{comment.text}</p></div>)}<form className="comment-composer" onSubmit={event => { event.preventDefault(); if (!draft.trim()) return; setComments(previous => ({ ...previous, [post.id]: [...(previous[post.id] ?? []), { author: 'Aria Malik', text: draft.trim() }] })); setDraft(''); }}><input aria-label={`Comment on ${post.title}`} placeholder="Add to the discussion…" value={draft} onChange={event => setDraft(event.target.value)} /><button disabled={!draft.trim()}>Post</button></form></div>}
  </article>)}</>;
}
