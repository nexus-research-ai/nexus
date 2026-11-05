'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import type { ForceGraphMethods, NodeObject } from 'react-force-graph-2d';
import { Network, Search, ZoomIn, ZoomOut, Maximize2, RefreshCw, X, ExternalLink, Focus, ArrowLeft } from 'lucide-react';
import { api, type GraphData, type GraphNode } from '@/lib/api';
import { safeOrigin } from '@/lib/editor';

const ForceGraph2D = dynamic(() => import('react-force-graph-2d').then(module => module.default<GraphNode>), { ssr: false });
const nodeColors = { faculty: '#2563eb', paper: '#0f766e', topic: '#b45309' };
const nodeLabels = { faculty: 'Faculty', paper: 'Paper', topic: 'Topic' };
type PositionedNode = GraphNode & { x: number; y: number };
type RenderLink = { source: string | GraphNode; target: string | GraphNode; relationship: string };
const endpointId = (endpoint: RenderLink['source']) => typeof endpoint === 'object' ? endpoint.id : endpoint;

interface GraphViewerProps {
  onSearchTopic?: (topic: string) => void;
  onAttachSource?: (sourceId: string) => void;
  attachedSourceIds?: string[];
  proposalOpen?: boolean;
}

export default function GraphViewer({ onSearchTopic, onAttachSource, attachedSourceIds = [], proposalOpen = false }: GraphViewerProps) {
  const [data, setData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [appliedQuery, setAppliedQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [cluster, setCluster] = useState('');
  const [centerId, setCenterId] = useState<string | null>(null);
  const [hops, setHops] = useState(1);
  const [limit, setLimit] = useState(300);
  const [refresh, setRefresh] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const canvasRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<ForceGraphMethods<GraphNode> | undefined>(undefined);
  const fitPending = useRef(true);
  const configuredGraph = useRef<object | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError('');
    api.graph(limit, appliedQuery || undefined, centerId || undefined, hops)
      .then(result => {
        if (!active) return;
        setData(result);
        setSelectedId(current => result.nodes.some(node => node.id === current) ? current : null);
        fitPending.current = true;
      })
      .catch(err => { if (active) setError(err instanceof Error ? err.message : 'Could not load the knowledge graph.'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [limit, appliedQuery, centerId, hops, refresh]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const observer = new ResizeObserver(([entry]) => {
      setDimensions({ width: Math.floor(entry.contentRect.width), height: Math.floor(entry.contentRect.height) });
      fitPending.current = true;
    });
    observer.observe(canvas);
    return () => observer.disconnect();
  }, []);

  // The renderer mutates nodes and link endpoints; keep that state separate from the response.
  const graphData = useMemo(() => {
    const nodes = data.nodes.filter(node => (typeFilter === 'all' || node.type === typeFilter) && (!cluster || node.cluster === cluster));
    const ids = new Set(nodes.map(node => node.id));
    return {
      nodes: nodes.map((node, index) => ({ ...node, x: Math.cos(index * 2.4) * Math.sqrt(index + 1) * 14, y: Math.sin(index * 2.4) * Math.sqrt(index + 1) * 14 })),
      links: data.links.filter(link => ids.has(endpointId(link.source)) && ids.has(endpointId(link.target)))
        .map(link => ({ ...link, source: endpointId(link.source), target: endpointId(link.target) })),
    };
  }, [data, typeFilter, cluster]);

  const areas = useMemo(() => [...new Set(data.nodes.map(node => node.cluster).filter((name): name is string => Boolean(name)))].sort(), [data]);
  const selectedNode = data.nodes.find(node => node.id === selectedId);
  const connections = useMemo(() => data.links.filter(link => endpointId(link.source) === selectedId || endpointId(link.target) === selectedId), [data, selectedId]);

  const fitGraph = useCallback(() => {
    graphRef.current?.zoomToFit(350, 48);
    fitPending.current = false;
  }, []);

  useEffect(() => {
    if (loading || dimensions.width <= 0 || dimensions.height <= 0) return;
    const timer = window.setTimeout(() => graphRef.current?.zoomToFit(250, 48), 150);
    return () => window.clearTimeout(timer);
  }, [dimensions.width, dimensions.height, loading]);

  const reset = () => {
    setQuery('');
    setAppliedQuery('');
    setTypeFilter('all');
    setCluster('');
    setCenterId(null);
    setSelectedId(null);
    fitPending.current = true;
  };

  const focusNode = (id: string) => {
    setTypeFilter('all');
    setCluster('');
    setAppliedQuery('');
    setQuery('');
    setCenterId(id);
  };

  const selectNode = (id: string) => {
    setSelectedId(id);
    const node = graphData.nodes.find(item => item.id === id);
    if (node?.x !== undefined && node.y !== undefined) graphRef.current?.centerAt(node.x, node.y, 350);
  };

  const drawNode = useCallback((node: GraphNode, ctx: CanvasRenderingContext2D, scale: number) => {
    const { x, y } = node as PositionedNode;
    if (!Number.isFinite(x) || !Number.isFinite(y)) return;
    const selected = node.id === selectedId;
    const baseRadius = node.type === 'faculty' ? 6 : node.type === 'topic' ? 5 : 3.5;
    const radius = Math.max(baseRadius, (selected ? 5 : node.type === 'paper' ? 2 : 3) / scale);
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fillStyle = nodeColors[node.type];
    ctx.fill();
    ctx.lineWidth = (selected ? 2 : 1) / scale;
    ctx.strokeStyle = selected ? '#17211f' : '#ffffff';
    ctx.stroke();
    if (selected || node.is_center || (scale > 1.6 && node.type !== 'paper')) {
      const fontSize = 12 / scale;
      const label = node.name.length > 40 ? `${node.name.slice(0, 38)}…` : node.name;
      ctx.font = `${selected ? 600 : 400} ${fontSize}px sans-serif`;
      const width = ctx.measureText(label).width;
      ctx.fillStyle = 'rgba(255,255,255,0.95)';
      ctx.fillRect(x - width / 2 - 3 / scale, y + radius + 2 / scale, width + 6 / scale, 18 / scale);
      ctx.fillStyle = '#253746';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(label, x, y + radius + 11 / scale);
    }
  }, [selectedId]);

  const hasFilters = Boolean(appliedQuery || cluster || typeFilter !== 'all' || centerId);

  return (
    <section className="knowledge-graph" aria-label="Knowledge graph explorer">
      <header className="kg-heading">
        <div><h1><Network size={21} /> Knowledge graph</h1><p>Explore how faculty, papers, and research topics connect.</p></div>
        <button type="button" className="kg-button" onClick={() => setRefresh(value => value + 1)} disabled={loading}><RefreshCw size={15} /> Refresh</button>
      </header>
      <div className="kg-toolbar">
        <form className="kg-search" onSubmit={event => { event.preventDefault(); setCenterId(null); setCluster(''); setTypeFilter('all'); setAppliedQuery(query.trim()); fitPending.current = true; }}>
          <label htmlFor="graph-search" className="sr-only">Search faculty, papers, or topics</label>
          <Search size={16} aria-hidden="true" />
          <input id="graph-search" value={query} onChange={event => setQuery(event.target.value)} placeholder="Search faculty, papers, or topics" />
          <button className="kg-button" type="submit" disabled={loading}>Search</button>
        </form>
        <label className="kg-field">Show<select aria-label="Record type" value={typeFilter} onChange={event => { setTypeFilter(event.target.value); setSelectedId(null); fitPending.current = true; }}>
          <option value="all">All record types</option><option value="faculty">Faculty</option><option value="paper">Papers</option><option value="topic">Topics</option>
        </select></label>
        <label className="kg-field">Research area<select aria-label="Research area" value={cluster} onChange={event => { setCluster(event.target.value); setSelectedId(null); fitPending.current = true; }}>
          <option value="">All areas</option>{areas.map(area => <option key={area} value={area}>{area.replace(/^Topic: /, '')}</option>)}
        </select></label>
        <label className="kg-field">Graph size<select aria-label="Graph size" value={limit} onChange={event => setLimit(Number(event.target.value))}>
          <option value={150}>150 records</option><option value={300}>300 records</option><option value={600}>600 records</option><option value={1200}>1,200 records</option><option value={2500}>2,500 records</option>
        </select></label>
        {hasFilters && <button className="kg-button" type="button" onClick={reset}>Reset filters</button>}
      </div>
      {centerId && <div className="kg-focus-bar"><span><Focus size={16} /> Connections to <strong>{data.center_node?.name || data.nodes.find(node => node.id === centerId)?.name || 'selected record'}</strong></span>
        <label>Connection depth <select aria-label="Connection depth" value={hops} onChange={event => setHops(Number(event.target.value))}><option value={1}>Direct connections</option><option value={2}>2 steps away</option><option value={3}>3 steps away</option></select></label>
        <button className="kg-button" type="button" onClick={reset}><ArrowLeft size={14} /> Full graph</button>
      </div>}
      <div className={`kg-body ${selectedNode ? 'has-selection' : ''}`}>
        <div className="kg-canvas" ref={canvasRef} aria-label="Interactive network. Select a record below to inspect it using the keyboard.">
          {!loading && !error && graphData.nodes.length > 0 && dimensions.width > 0 && dimensions.height > 0 && <ForceGraph2D
            ref={graphRef} width={dimensions.width} height={dimensions.height} graphData={graphData}
            nodeCanvasObject={drawNode} nodeLabel={node => `${nodeLabels[node.type]}: ${node.name}`}
            nodePointerAreaPaint={(node, color, ctx) => { ctx.fillStyle = color; ctx.beginPath(); ctx.arc(node.x ?? 0, node.y ?? 0, 9, 0, Math.PI * 2); ctx.fill(); }}
            linkColor={() => '#c3ced8'} linkWidth={0.7} backgroundColor="#fbfcfe"
            cooldownTicks={130} onEngineTick={() => {
              const graph = graphRef.current;
              if (!graph || configuredGraph.current === graphData) return;
              configuredGraph.current = graphData;
              graph.d3Force('charge')?.strength(-80);
              graph.d3Force('link')?.distance(55).strength(0.15);
              // Keep isolated records near the network instead of letting them set the camera bounds.
              graph.d3Force('position', (alpha: number) => {
                for (const node of graphData.nodes as NodeObject<GraphNode>[]) {
                  node.vx = (node.vx ?? 0) - (node.x ?? 0) * alpha * 0.035;
                  node.vy = (node.vy ?? 0) - (node.y ?? 0) * alpha * 0.035;
                }
              });
            }} onEngineStop={() => { if (fitPending.current) fitGraph(); }}
            onNodeClick={node => setSelectedId(node.id)} onBackgroundClick={() => setSelectedId(null)}
          />}
          {loading && <div className="kg-message" role="status"><div className="spinner" /><strong>Loading the graph…</strong><span>Finding research records and their connections.</span></div>}
          {error && !loading && <div className="kg-message" role="alert"><Network size={30} /><strong>The graph couldn’t load</strong><span>{error}</span><button className="kg-button" onClick={() => setRefresh(value => value + 1)}>Try again</button></div>}
          {!loading && !error && !graphData.nodes.length && <div className="kg-message" role="status"><Search size={28} /><strong>No matching records</strong><span>{hasFilters ? 'Try a broader search or reset your filters.' : 'Import research records to start exploring connections.'}</span>{hasFilters && <button className="kg-button" onClick={reset}>Reset filters</button>}</div>}
          {!loading && !error && graphData.nodes.length > 0 && <div className="kg-map-controls" aria-label="Graph zoom controls">
            <button type="button" className="icon-button" aria-label="Zoom in" onClick={() => { const graph = graphRef.current; if (graph) graph.zoom(graph.zoom() * 1.3, 200); }}><ZoomIn size={17} /></button>
            <button type="button" className="icon-button" aria-label="Zoom out" onClick={() => { const graph = graphRef.current; if (graph) graph.zoom(graph.zoom() / 1.3, 200); }}><ZoomOut size={17} /></button>
            <button type="button" className="icon-button" aria-label="Fit graph to view" onClick={fitGraph}><Maximize2 size={17} /></button>
          </div>}
        </div>
        {selectedNode && !loading && <aside className="kg-details" aria-label="Record details">
          <div className="kg-detail-heading"><span className="kg-kind"><i style={{ background: nodeColors[selectedNode.type] }} />{nodeLabels[selectedNode.type]}</span><button className="icon-button" aria-label="Close record details" onClick={() => setSelectedId(null)}><X size={16} /></button></div>
          <h2>{selectedNode.name}</h2>
          {selectedNode.evidence_kind === 'synthetic' && <p className="kg-sample">Example record</p>}
          <dl>{selectedNode.cluster && <div><dt>Research area</dt><dd>{selectedNode.cluster.replace(/^Topic: /, '')}</dd></div>}
            {(['department', 'year', 'faculty_author', 'doi'] as const).map(key => selectedNode.metadata?.[key] ? <div key={key}><dt>{{ department: 'Department', year: 'Published', faculty_author: 'Faculty author', doi: 'DOI' }[key]}</dt><dd>{String(selectedNode.metadata[key])}</dd></div> : null)}
          </dl>
          {selectedNode.metadata?.abstract && <div className="kg-abstract"><h3>Abstract</h3><p>{String(selectedNode.metadata.abstract)}</p></div>}
          {safeOrigin(selectedNode.origin ?? '') && <a className="kg-source" href={safeOrigin(selectedNode.origin ?? '')} target="_blank" rel="noopener noreferrer">View original source <ExternalLink size={14} /></a>}
          <button className="kg-button kg-primary" onClick={() => focusNode(selectedNode.id)} disabled={centerId === selectedNode.id}><Focus size={15} />{centerId === selectedNode.id ? 'Showing connections' : 'Explore connections'}</button>
          {selectedNode.type === 'topic' && onSearchTopic && <button className="kg-button" onClick={() => onSearchTopic(selectedNode.name)}>Search this topic</button>}
          {selectedNode.type !== 'topic' && onAttachSource && proposalOpen && <button className="kg-button" disabled={attachedSourceIds.includes(selectedNode.id)} onClick={() => onAttachSource(selectedNode.id)}>{attachedSourceIds.includes(selectedNode.id) ? 'Attached to proposal' : 'Attach to proposal'}</button>}
          <h3>Connections in this graph ({connections.length})</h3>
          <div className="kg-connections">{connections.slice(0, 30).map((link, index) => {
            const id = endpointId(link.source) === selectedNode.id ? endpointId(link.target) : endpointId(link.source);
            const other = data.nodes.find(node => node.id === id);
            return other ? <button key={`${id}-${index}`} type="button" onClick={() => { setTypeFilter('all'); setCluster(''); selectNode(id); }}><span>{other.name}</span><small>{link.relationship.replaceAll('_', ' ')}</small></button> : null;
          })}{!connections.length && <p>No connections in the loaded records. Try increasing the graph size.</p>}{connections.length > 30 && <p>Showing 30 connections. Explore this record to see its neighborhood.</p>}</div>
        </aside>}
      </div>
      <footer className="kg-footer"><div className="kg-legend">{Object.entries(nodeLabels).map(([key, label]) => <span key={key}><i style={{ background: nodeColors[key as keyof typeof nodeColors] }} />{label === 'Paper' ? 'Papers' : label === 'Topic' ? 'Topics' : label}</span>)}</div><span role="status">{loading ? 'Loading…' : `${graphData.nodes.length.toLocaleString()} records · ${graphData.links.length.toLocaleString()} connections`}</span><span>Scroll to zoom. Drag to pan. Select a record for details.</span></footer>
      {!loading && !error && graphData.nodes.length > 0 && <details className="kg-record-list"><summary>Browse records as a list ({graphData.nodes.length})</summary><div>{graphData.nodes.map(node => <button key={node.id} type="button" onClick={() => selectNode(node.id)} aria-pressed={selectedId === node.id}><span>{node.name}</span><small>{nodeLabels[node.type]}</small></button>)}</div></details>}
    </section>
  );
}
