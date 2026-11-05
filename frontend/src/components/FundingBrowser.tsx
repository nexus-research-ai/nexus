'use client';

import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, Bookmark, CalendarDays, Check, ExternalLink, Search } from 'lucide-react';

type FundingOpportunity = {
  id: string;
  agency: string;
  solicitation_number: string;
  title: string;
  award_ceiling_usd: number;
  deadline: string;
  focus_areas: string[];
  eligibility: string[];
  description: string;
};
const savedKey = 'nexus.saved-funding.v1';
const agencyWebsites: Record<string, string> = { NSF: 'https://www.nsf.gov', NIH: 'https://www.nih.gov', DARPA: 'https://www.darpa.mil' };
const currency = (amount: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(amount);
const deadlineDate = (value: string) => new Date(`${value.slice(0, 10)}T23:59:59`);
const dateLabel = (value: string) => deadlineDate(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

export default function FundingBrowser() {
  const [opportunities, setOpportunities] = useState<FundingOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refresh, setRefresh] = useState(0);
  const [query, setQuery] = useState('');
  const [agency, setAgency] = useState('all');
  const [deadline, setDeadline] = useState('all');
  const [sort, setSort] = useState('deadline');
  const [savedOnly, setSavedOnly] = useState(false);
  const [savedIds, setSavedIds] = useState<string[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showMobileDetail, setShowMobileDetail] = useState(false);
  const [notice, setNotice] = useState<{ id: string; message: string } | null>(null);

  useEffect(() => {
    try {
      const saved: unknown = JSON.parse(localStorage.getItem(savedKey) || '[]');
      if (Array.isArray(saved)) setSavedIds(saved.filter((id): id is string => typeof id === 'string'));
    } catch { /* A blocked or invalid local store does not prevent browsing. */ }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError('');
    fetch('/api/v1/funding/opportunities', { signal: controller.signal })
      .then(async response => {
        if (!response.ok) throw new Error('The funding catalog is unavailable. Try again in a moment.');
        const result = await response.json();
        if (!Array.isArray(result.opportunities)) throw new Error('The funding catalog returned an unexpected response.');
        if (!controller.signal.aborted) setOpportunities(result.opportunities);
      })
      .catch(err => { if (!controller.signal.aborted) setError(err instanceof Error ? err.message : 'Could not load funding opportunities.'); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [refresh]);

  const filtered = useMemo(() => {
    const now = new Date();
    const end = new Date(now.getTime() + Number(deadline) * 86400000);
    const text = query.trim().toLowerCase();
    return opportunities.filter(item => {
      const due = deadlineDate(item.deadline);
      return (agency === 'all' || agency === item.agency)
        && (!savedOnly || savedIds.includes(item.id))
        && (deadline === 'all' || (due >= now && due <= end))
        && (!text || [item.title, item.agency, item.solicitation_number, item.description, ...item.focus_areas].join(' ').toLowerCase().includes(text));
    }).sort((a, b) => sort === 'amount' ? b.award_ceiling_usd - a.award_ceiling_usd : a.deadline.localeCompare(b.deadline));
  }, [opportunities, agency, deadline, query, sort, savedOnly, savedIds]);

  const selected = filtered.find(item => item.id === selectedId) ?? filtered[0];
  const clearFilters = () => { setQuery(''); setAgency('all'); setDeadline('all'); setSavedOnly(false); setShowMobileDetail(false); };
  const toggleSaved = (item: FundingOpportunity) => {
    const isSaved = savedIds.includes(item.id);
    const next = isSaved ? savedIds.filter(id => id !== item.id) : [...savedIds, item.id];
    try {
      localStorage.setItem(savedKey, JSON.stringify(next));
      setSavedIds(next);
      setNotice({ id: item.id, message: isSaved ? 'Opportunity removed from your saved list.' : 'Opportunity saved in this browser.' });
    } catch { setNotice({ id: item.id, message: 'Could not save this opportunity. Allow browser storage and try again.' }); }
  };

  return <div className={`funding-browser ${showMobileDetail && selected ? 'funding-detail-open' : ''}`}>
    <div className="funding-intro"><p>Find a grant, review the requirements, and save opportunities to revisit.</p><p className="funding-catalog-note">Example catalog. Confirm current deadlines, award amounts, and eligibility on the agency website before applying.</p></div>
    <div className="funding-browser-filters">
      <label className="funding-search"><span className="sr-only">Search funding opportunities</span><Search size={17} aria-hidden="true" /><input type="search" value={query} onChange={event => setQuery(event.target.value)} placeholder="Search by keyword or grant name" /></label>
      <label>Agency<select aria-label="Agency" value={agency} onChange={event => setAgency(event.target.value)}><option value="all">All agencies</option>{[...new Set(opportunities.map(item => item.agency))].sort().map(name => <option key={name}>{name}</option>)}</select></label>
      <label>Deadline<select aria-label="Deadline" value={deadline} onChange={event => setDeadline(event.target.value)}><option value="all">Any date</option><option value="30">Next 30 days</option><option value="90">Next 90 days</option></select></label>
      <button className={`funding-saved-toggle ${savedOnly ? 'active' : ''}`} aria-pressed={savedOnly} onClick={() => setSavedOnly(value => !value)}><Bookmark size={15} />Saved ({savedIds.length})</button>
    </div>
    <div className="funding-browser-content">
      <section className="funding-results" aria-label="Funding opportunities">
        <header className="funding-results-header"><span role="status">{loading ? 'Loading opportunities…' : `${filtered.length} ${filtered.length === 1 ? 'opportunity' : 'opportunities'}`}</span><label>Sort by<select aria-label="Sort by" value={sort} onChange={event => setSort(event.target.value)}><option value="deadline">Soonest deadline</option><option value="amount">Largest award</option></select></label></header>
        {loading && <div className="funding-empty" role="status"><div className="spinner" /><p>Loading the funding catalog…</p></div>}
        {!loading && error && <div className="funding-empty" role="alert"><h3>Funding couldn’t load</h3><p>{error}</p><button className="kg-button" onClick={() => setRefresh(value => value + 1)}>Try again</button></div>}
        {!loading && !error && !filtered.length && <div className="funding-empty"><Search size={28} /><h3>No matching opportunities</h3><p>{savedOnly ? 'Save an opportunity to find it here, or browse all funding.' : 'Try another keyword, agency, or deadline.'}</p><button className="kg-button" onClick={clearFilters}>Clear filters</button></div>}
        {!loading && !error && filtered.map(item => <button type="button" key={item.id} className={`funding-result ${selected?.id === item.id ? 'selected' : ''}`} aria-pressed={selected?.id === item.id} onClick={() => { setSelectedId(item.id); setShowMobileDetail(true); }}>
          <span className="funding-result-top"><span className="funding-agency">{item.agency}</span>{savedIds.includes(item.id) && <span className="funding-is-saved"><Bookmark size={13} />Saved</span>}</span>
          <strong>{item.title}</strong><p>{item.description}</p>
          <span className="funding-result-facts"><span>Up to <b>{currency(item.award_ceiling_usd)}</b></span><span><CalendarDays size={14} />{dateLabel(item.deadline)}</span></span>
        </button>)}
      </section>
      {!loading && !error && selected && <aside className="funding-opportunity-detail" aria-label="Opportunity details">
        <button className="funding-back kg-button" onClick={() => setShowMobileDetail(false)}><ArrowLeft size={15} />Back to opportunities</button>
        <span className="funding-agency">{selected.agency} · {selected.solicitation_number}</span>
        <h3>{selected.title}</h3><p>{selected.description}</p>
        <dl className="funding-key-facts"><div><dt>Maximum award</dt><dd>{currency(selected.award_ceiling_usd)}</dd></div><div><dt>Application deadline</dt><dd>{dateLabel(selected.deadline)}</dd></div></dl>
        <section><h4>Who can apply</h4><ul>{selected.eligibility.map(item => <li key={item}>{item}</li>)}</ul></section>
        <section><h4>Research areas</h4><div className="funding-area-tags">{selected.focus_areas.map(item => <span key={item}>{item}</span>)}</div></section>
        <div className="funding-detail-actions"><button className={`kg-button ${savedIds.includes(selected.id) ? '' : 'kg-primary'}`} onClick={() => toggleSaved(selected)}>{savedIds.includes(selected.id) ? <Check size={16} /> : <Bookmark size={16} />}{savedIds.includes(selected.id) ? 'Saved · remove' : 'Save opportunity'}</button>
          {agencyWebsites[selected.agency] && <a className="kg-button" href={agencyWebsites[selected.agency]} target="_blank" rel="noopener noreferrer">Visit {selected.agency} website<ExternalLink size={15} /></a>}
        </div><p className="funding-save-help">Saved opportunities stay in this browser. Saving does not start an application.</p>
        {notice?.id === selected.id && <p className="funding-save-notice" role="status">{notice.message}</p>}
      </aside>}
    </div>
  </div>;
}
