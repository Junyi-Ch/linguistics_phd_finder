// Build-time only (runs in Node during `astro build`): who works on similar things, and a map layout.
// Similarity = cosine between the same research-profile vectors the matcher uses (public/search/vectors.i8.bin).
import fs from 'node:fs';
import path from 'node:path';
import { forceSimulation, forceCollide } from 'd3-force';
import { UMAP } from 'umap-js';
import faculty from '../data/faculty.json';
import programs from '../data/programs.json';
import { GROUPS, type Faculty, type Program } from './data';

export type Related = { i: number; id: string; s: number; shared: string[] };
export type Co = { i: number; id: string; n: number; y: number; t: string };
type Net = { F: Faculty[]; related: Related[][]; edges: [number, number][]; xy: [number, number][]; groups: number[]; co: Co[][]; coEdges: [number, number, number][]; oa: Record<string, string[]>; coBuilt: string | null; phd: Record<string, { inst: string; year: number | null }>; adv: (number | string)[][]; stu: (number | string)[][]; sib: [number, string][][]; wd: Record<string, string> };

const K = 8;   // neighbours kept per person
const EK = 4;  // neighbours drawn as links on the map
let cache: Net | null = null;

/** OpenAlex sometimes has garbled titles from bad scans; only show ones that read like text */
function readable(t: string) {
  if (!t || /[$\\{}<>|^~]/.test(t)) return false;
  const letters = t.replace(/[^A-Za-z]/g, '');
  if (letters.length < 4) return /\p{L}/u.test(t);
  const vowels = letters.replace(/[^aeiouyAEIOUY]/g, '').length;
  return vowels / letters.length > 0.25;
}

export function groupOf(f: Faculty): number {
  const t = f.labels?.topic || [];
  const main = t.find((l) => l.p) || t[0];
  if (!main) return -1;
  return GROUPS.findIndex((g) => (g.topics as readonly string[]).includes(main.c));
}

export function network(): Net {
  if (cache) return cache;
  const F = faculty as Faculty[];
  const root = process.cwd();
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'public/search/manifest.json'), 'utf8'));
  const ids: string[] = JSON.parse(fs.readFileSync(path.join(root, 'public/search/index.json'), 'utf8'));
  const buf = fs.readFileSync(path.join(root, 'public/search/vectors.i8.bin'));
  const raw = new Int8Array(buf.buffer, buf.byteOffset, buf.byteLength);
  const D: number = manifest.dimensions;
  const row = new Map(ids.map((id, i) => [id, i]));
  const n = F.length;
  const V = F.map((f) => {
    const a = new Float32Array(D);
    const r = row.get(f.id);
    if (r == null) return a;
    let ss = 0;
    for (let j = 0; j < D; j++) { a[j] = raw[r * D + j]; ss += a[j] * a[j]; }
    const k = 1 / Math.sqrt(ss || 1);
    for (let j = 0; j < D; j++) a[j] *= k;
    return a;
  });
  const S = new Float32Array(n * n);
  for (let i = 0; i < n; i++) {
    const a = V[i];
    for (let j = i + 1; j < n; j++) {
      const b = V[j]; let s = 0;
      for (let d = 0; d < D; d++) s += a[d] * b[d];
      S[i * n + j] = s; S[j * n + i] = s;
    }
  }
  const topics = F.map((f) => (f.labels?.topic || []).map((l) => l.c));
  const related: Related[][] = F.map((_, i) => {
    const cand: { j: number; s: number }[] = [];
    for (let j = 0; j < n; j++) if (j !== i) cand.push({ j, s: S[i * n + j] });
    cand.sort((x, y) => y.s - x.s);
    return cand.slice(0, K).map(({ j, s }) => ({ i: j, id: F[j].id, s: Math.round(s * 1000) / 1000, shared: topics[i].filter((c) => topics[j].includes(c)) }));
  });
  const seen = new Set<string>();
  const edges: [number, number][] = [];
  related.forEach((list, i) => list.slice(0, EK).forEach((r) => {
    const a = Math.min(i, r.i), b = Math.max(i, r.i), key = a + ':' + b;
    if (seen.has(key)) return;
    seen.add(key); edges.push([a, b]);
  }));
  // Map layout: UMAP on the profile vectors (seeded, so every build gives the same map), then nudge dots apart.
  let seed = 7;
  const rand = () => { seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  const emb = new UMAP({ nComponents: 2, nNeighbors: 12, minDist: 0.35, spread: 1, random: rand }).fit(V.map((a) => Array.from(a)));
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
  for (const [x, y] of emb) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
  const sc = 520 / Math.max(x1 - x0, y1 - y0);
  const nodes = emb.map(([x, y]) => ({ x: (x - (x0 + x1) / 2) * sc, y: (y - (y0 + y1) / 2) * sc }));
  const sim = forceSimulation(nodes as any).alphaDecay(0.05).velocityDecay(0.5).force('collide', forceCollide(3.2)).stop();
  for (let t = 0; t < 120; t++) sim.tick();
  const xy = nodes.map((p) => [Math.round((p.x || 0) * 10) / 10, Math.round((p.y || 0) * 10) / 10] as [number, number]);
  // co-authors from OpenAlex (pipeline/coauthors.py); optional
  const co: Co[][] = F.map(() => []);
  const coEdges: [number, number, number][] = [];
  let oa: Record<string, string[]> = {}, coBuilt: string | null = null;
  const cp = path.join(root, 'src/data/coauthors.json');
  if (fs.existsSync(cp)) {
    const d = JSON.parse(fs.readFileSync(cp, 'utf8'));
    const at = new Map(F.map((f, i) => [f.id, i]));
    oa = d.authors || {}; coBuilt = d.built || null;
    for (const [a, b, n, y, t] of d.pairs as [string, string, number, number, string][]) {
      const ia = at.get(a), ib = at.get(b);
      if (ia == null || ib == null) continue;
      const tt = readable(t) ? t : '';
      co[ia].push({ i: ib, id: b, n, y, t: tt }); co[ib].push({ i: ia, id: a, n, y, t: tt });
      coEdges.push([ia, ib, n]);
    }
    co.forEach((l) => l.sort((x, y) => y.n - x.n || y.y - x.y));
  }
  // academic family (pipeline/tree.py): PhD school and year, advisor -> student links; optional
  let phd: Record<string, { inst: string; year: number | null }> = {}, wd: Record<string, string> = {};
  const adv: (number | string)[][] = F.map(() => []), stu: (number | string)[][] = F.map(() => []);
  const sib: [number, string][][] = F.map(() => []);
  const nkey = (n: string) => { const t = n.normalize('NFKD').replace(/[^\x00-\x7f]/g, '').toLowerCase().replace(/[^a-z ]/g, ' ').split(/\s+/).filter(Boolean); return t.length >= 2 ? t[0] + ' ' + t[t.length - 1] : n; };
  const tp = path.join(root, 'src/data/tree.json');
  if (fs.existsSync(tp)) {
    const d = JSON.parse(fs.readFileSync(tp, 'utf8'));
    const at = new Map(F.map((f, i) => [f.id, i]));
    phd = d.phd || {}; wd = d.wikidata || {};
    for (const [s, sn, a, an] of d.advising as [string | null, string | null, string | null, string | null][]) {
      const is = s ? at.get(s) : undefined, ia = a ? at.get(a) : undefined;
      if (is != null) adv[is].push(ia != null ? ia : (an || ''));
      if (ia != null) stu[ia].push(is != null ? is : (sn || ''));
    }
    // academic siblings: people on the site who share an advisor (on the site or not)
    const groups = new Map<string, { label: string; kids: Set<number> }>();
    F.forEach((_, i) => adv[i].forEach((a) => {
      const k = typeof a === 'number' ? 'id:' + a : 'n:' + nkey(a);
      const label = typeof a === 'number' ? F[a].name : a;
      if (!groups.has(k)) groups.set(k, { label, kids: new Set() });
      groups.get(k)!.kids.add(i);
    }));
    for (const { label, kids } of groups.values()) for (const i of kids) for (const j of kids) if (i !== j && !sib[i].some(([x]) => x === j)) sib[i].push([j, label]);
  }
  cache = { F, related, edges, xy, groups: F.map(groupOf), co, coEdges, oa, coBuilt, phd, adv, stu, sib, wd };
  return cache;
}

export function relatedFor(id: string): (Related & { f: Faculty; p?: Program })[] {
  const net = network();
  const i = net.F.findIndex((f) => f.id === id);
  if (i < 0) return [];
  const P = programs as Program[];
  return net.related[i].map((r) => ({ ...r, f: net.F[r.i], p: P.find((p) => p.slug === net.F[r.i].u) }));
}

export function coauthorsFor(id: string): (Co & { f: Faculty; p?: Program })[] {
  const net = network();
  const i = net.F.findIndex((f) => f.id === id);
  if (i < 0) return [];
  const P = programs as Program[];
  return net.co[i].map((c) => ({ ...c, f: net.F[c.i], p: P.find((p) => p.slug === net.F[c.i].u) }));
}
export const openalexFor = (id: string) => network().oa[id]?.[0] || null;
export const coauthorsBuilt = () => network().coBuilt;

/** PhD school + year, advisors and students (people on the site come with their record), and others with the same PhD school */
export function familyFor(id: string) {
  const net = network();
  const i = net.F.findIndex((f) => f.id === id);
  if (i < 0) return null;
  const P = programs as Program[];
  const who = (x: number | string) => (typeof x === 'number' ? { f: net.F[x], p: P.find((p) => p.slug === net.F[x].u) } : { name: x });
  const phd = net.phd[id] || null;
  return { phd, phdProgram: phd ? P.find((p) => p.name === phd.inst) : undefined, advisors: net.adv[i].map(who), students: net.stu[i].map(who), siblings: net.sib[i].map(([j, via]) => ({ f: net.F[j], p: P.find((p) => p.slug === net.F[j].u), via })), wd: net.wd[id] || null };
}

/** compact JSON for the Network page */
export function networkJson() {
  const net = network();
  const P = new Map((programs as Program[]).map((p) => [p.slug, p]));
  return {
    nodes: net.F.map((f, i) => ({
      id: f.id, n: f.name, u: f.u, us: P.get(f.u)?.short || f.u, r: f.rank, fld: f.fld,
      g: net.groups[i], x: net.xy[i][0], y: net.xy[i][1], s: f.summary, sz: f.summary_zh || '',
      k: net.related[i].map((r) => [r.i, r.shared]),
      c: net.co[i].map((c) => [c.i, c.n, c.y]),
      ph: net.phd[f.id] ? [net.phd[f.id].inst, net.phd[f.id].year] : null,
      av: net.adv[i], st: net.stu[i], sb: net.sib[i],
    })),
    edges: net.edges,
    co: net.coEdges,
  };
}
