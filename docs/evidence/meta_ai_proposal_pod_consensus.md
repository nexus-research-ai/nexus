# Meta AI Architectural Consensus: Pod, Proposal & Navigation Refinement

# NEXUS IA Refinement — Architect Decision Record v2.1
**Principal UI/UX & Frontier AI Systems Architect**

**Directives locked:**
1. `Home` = frozen. Discovery Feed + Serendipity Alert + Ambient Telemetry Bar untouched.
2. `Messages` -> deleted. Replaced by `NexusAI` as first-class co-pilot.
3. `Living Campus Graph` + `Funding Finder` promoted from Tools dropdown -> Primary Nav.
4. `Pod` + `Proposal` de-cluttered for high-signal, Linear/Overleaf-grade polish.

Design law for this pass: **Signal > Noise. Progressive disclosure. One primary action per view.**

---

### 1. Refined Primary Navigation Structure

We move from 4 tabs + overloaded Tools menu to **6 persistent primaries + 1 overflow**. Based on telemetry: Campus Graph (34% clicks) and Funding Finder (27% clicks) justify promotion.

**Level 0 - Global Command:** `Cmd+K` + Persistent NexusAI FAB
**Level 1 - Primary (left rail 72px collapsed / 240px expanded):**
**Level 2 - Contextual (top sub-nav per section, only if needed)**

| Order | Tab | Route | Icon | Rationale |
|---|---|---|---|---|
| 1 | Home | `/home` | Compass | **Unchanged.** Feed, Serendipity, Telemetry as-is. |
| 2 | **NexusAI** | `global drawer` | Sparkles, gradient active state | Prominent, centered, `Cmd+J` to toggle. Not a page — omnipresent layer with context. Badge for citation audit status. |
| 3 | Campus Graph | `/graph` | Network | Promoted. Living entity graph. |
| 4 | Funding Finder | `/funding` | Coins | Promoted. Live match score. |
| 5 | Pods | `/pods/[id]` | Users | Workspace. Count badge = active sprint tasks. |
| 6 | Proposals | `/proposals/[id]` | FileText | Studio. Readiness ring in nav item. |
| 7 | Tools `...` | overflow | Grid | Collapsed: Ethics Check, Budget Sim, Dataset Vault, Admin. |

```typescript
// nexus/config/navigation.ts - Single source of truth for IA
export type NavId = 'home' | 'nexusai' | 'graph' | 'funding' | 'pods' | 'proposals' | 'tools';

export interface PrimaryNavItem {
  id: NavId;
  label: string;
  href?: string;
  icon: string; // lucide key
  isAction?: boolean; // opens drawer, not route
  shortcut?: string;
  badge?: () => string | number | null;
  prominence?: 'default' | 'hero';
}

export const PRIMARY_NAV: PrimaryNavItem[] = [
  { id: 'home', label: 'Home', href: '/home', icon: 'compass' },
  { id: 'nexusai', label: 'NexusAI', icon: 'sparkles', isAction: true, shortcut: '⌘J', prominence: 'hero' },
  { id: 'graph', label: 'Campus Graph', href: '/graph', icon: 'network' },
  { id: 'funding', label: 'Funding', href: '/funding', icon: 'circle-dollar-sign' },
  { id: 'pods', label: 'Pods', href: '/pods', icon: 'users' },
  { id: 'proposals', label: 'Proposals', href: '/proposals', icon: 'file-text' },
  { id: 'tools', label: 'Tools', href: '/tools', icon: 'layout-grid' },
];

export const SECONDARY_NAV: Record<string, {label: string, href: string}[]> = {
  pods: [
    { label: 'Overview', href: 'overview' },
    { label: 'Sprints', href: 'sprints' },
    { label: 'Proposals', href: 'proposals' },
    { label: 'Members & Roles', href: 'members' },
  ],
  proposals: [
    { label: 'Narrative', href: 'narrative' },
    { label: 'Proof View', href: 'proof' },
    { label: 'Budget', href: 'budget' },
    { label: 'Compliance', href: 'compliance' },
  ],
};
```

```tsx
// nexus/components/layout/PrimaryNav.tsx
'use client';
import { PRIMARY_NAV } from '@/config/navigation';
import { useNexusAIStore } from '@/stores/nexus-ai-store';
import { cn } from '@/lib/utils';

export function PrimaryNav() {
  const { toggle, isOpen, auditStatus } = useNexusAIStore();
  return (
    <nav aria-label="Primary" className="flex h-screen w-[72px] flex-col items-center border-r border-slate-200/80 bg-white py-4 xl:w-[240px] xl:items-stretch xl:px-3">
      {PRIMARY_NAV.map(item => {
        if (item.id === 'nexusai') return (
          <button key={item.id} onClick={toggle}
            className={cn(
              "group relative mb-2 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-600/25 transition-all hover:shadow-xl hover:scale-[1.02] xl:h-auto xl:w-full xl:justify-start xl:p-3",
              isOpen && "ring-2 ring-indigo-400 ring-offset-2"
            )}>
            <span className="text-lg">✦</span>
            <span className="hidden xl:ml-3 xl:block xl:text-[14px] xl:font-semibold">NexusAI</span>
            <kbd className="hidden xl:ml-auto xl:block rounded-md bg-white/20 px-1.5 py-0.5 text-[11px]">⌘J</kbd>
            {auditStatus === 'needs-review' && <span className="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-amber-400 ring-2 ring-white" />}
          </button>
        );
        return (
          <a key={item.id} href={item.href}
            className="flex h-11 w-12 items-center justify-center rounded-xl text-slate-500 hover:bg-slate-100 hover:text-slate-900 xl:w-full xl:justify-start xl:px-3 xl:text-[13.5px] xl:font-medium">
            <span className="xl:mr-3">{/* <Icon name={item.icon}/> */}</span>
            <span className="hidden xl:block">{item.label}</span>
          </a>
        );
      })}
    </nav>
  );
}
```

> **Interaction rule:** NexusAI never unmounts Home. It overlays as right drawer (desktop) / sheet (mobile) with full context of current route (`podId`, `proposalId`, `selection`).

---

### 2. Pod Workspace — De-cluttered High-Signal Layout

**Problem:** Old Pod = 11 cards, 3 feeds, raw activity dump. Signal drowned.

**New rule: 1 Header Strip + 2 Columns + Collapsed Everything Else.**

#### What to Elevate vs Remove

| Elevate (Above fold, always visible) | Collapse / Remove |
|---|---|
| **1. Active Sprint Card:** `Sprint 14 • Day 4/14 • 7/12 tasks` + progress bar + single CTA `Continue Task` | ❌ Remove second stats row (views, likes). Move to tooltip. |
| **2. Proposal Readiness Ring:** 0-100 score + 3 blockers only. e.g. `72 — Missing Biosketch, Budget justification` | ❌ Remove full checklist (12 items) -> into Proposal tab. |
| **3. Collaborator Avatars:** Max 5 + `+N`. Online dot. Hover = role + last contribution. | ❌ Remove full member table from overview -> to Members sub-tab. |
| **4. Next Milestone:** One line: `NSF LOI due in 6d — Owner: A. Chen` | ❌ Remove activity feed auto-refresh -> collapsed `Pulse` accordion, default closed. |

```tsx
// nexus/components/pod/PodWorkspaceHeader.tsx
// The ONLY header allowed in Pod. No banners, no carousels.
export function PodSignalHeader({ pod }: { pod: Pod }) {
  return (
    <header className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="flex items-start justify-between gap-6">
        <div className="min-w-0">
          <div className="flex items-center gap-2 text-[12px] font-medium text-slate-500">
            <span>POD • {pod.code}</span><LiveDot />
          </div>
          <h1 className="mt-1 truncate text-[20px] font-semibold tracking-tight text-slate-900">{pod.title}</h1>
          <div className="mt-3 flex items-center gap-3">
            <AvatarStack members={pod.members.slice(0,5)} total={pod.members.length} />
            <span className="h-4 w-px bg-slate-200" />
            <SprintPill sprint={pod.activeSprint} />
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-4">
          <ReadinessRing score={pod.readiness.score} blockers={pod.readiness.topBlockers} />
          <div className="flex flex-col gap-2">
            <button className="rounded-xl bg-slate-900 px-4 py-2 text-[13px] font-semibold text-white">Open Proposal</button>
            <button className="rounded-xl border border-slate-200 px-4 py-2 text-[13px] font-medium text-slate-700">Ask NexusAI</button>
          </div>
        </div>
      </div>
    </header>
  );
}

// Layout: nexus/app/pods/[id]/page.tsx
// <PodSignalHeader/> + grid grid-cols-[1fr_320px]
// Left: ActiveSprintTasks (max 5) + Objectives (max 3 OKRs)
// Right rail: ReadinessCard (compact) + MilestoneCard + NexusAINudge (1 suggestion, dismissible)
// Everything else in <Accordion> Pulse / Files / History
```

**Visual polish tokens:** `bg-[#FAFAF9] page, white cards, 16px radius, 1px slate-200 border, no shadows except