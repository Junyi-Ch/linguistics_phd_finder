export const DIMS = ['topic', 'approach', 'data', 'setting', 'region'] as const;
export type Dim = (typeof DIMS)[number];
// Kind of unit a faculty member sits in: a Linguistics department, or one of the adjacent fields.
export const FIELDS = ['LING', 'COMP', 'APPLIED', 'LANG', 'SPEECH'] as const;
export type Field = (typeof FIELDS)[number];
export const FIELD_LABELS: Record<Field, { en: string; zh: string }> = {
  LING: { en: 'Linguistics departments', zh: '语言学系' },
  COMP: { en: 'Computational linguistics & NLP', zh: '计算语言学与 NLP' },
  APPLIED: { en: 'Applied linguistics & SLA', zh: '应用语言学与二语习得' },
  LANG: { en: 'Language-department linguistics', zh: '语种系中的语言学' },
  SPEECH: { en: 'Speech, hearing & cognitive science', zh: '言语听力与认知科学' },
};
export const fieldLabel = (f: Field, lang: string) => (lang === 'zh' ? FIELD_LABELS[f]?.zh : FIELD_LABELS[f]?.en) || f;
export type LabelRef = { c: string; p: boolean };
export type Faculty = {
  id: string; name: string; u: string; dept: string; rank: string; title: string;
  profile: string | null; site: string | null; scholar: string | null;
  areas: string[]; summary: string; summary_zh: string; conf: string;
  labels: Record<Dim, LabelRef[]>; kw: string[]; src: string[]; scraped: string | null; v: number; fld: Field;
};
export type Unit = { name: string; field: Field; school: string | null; url: string | null; phd: string | null; phd_url: string | null; directory: string | null };
export type Program = {
  slug: string; name: string; short: string; city: string; state: string; lat: number; lng: number;
  domain: string | null; logo: string | null; guide: string[]; units: Unit[];
  n: number; ranks: Record<string, number>; notes: string;
  qs: string | null; us: string | null;
};
// School rankings, shown as a rough guide only (see the About page)
export const RANKINGS = {
  qs: { name: 'QS World University Rankings by Subject 2026: Linguistics', short: 'QS Linguistics 2026', url: 'https://www.topuniversities.com/university-subject-rankings/linguistics', tops: [25, 50, 100, 200, 350] },
  us: { name: 'U.S. News Best National Universities 2027', short: 'U.S. News 2027 (whole university)', url: 'https://www.usnews.com/best-colleges/rankings/national-universities', tops: [25, 50, 100] },
} as const;
/** worst position a rank can mean: "17" -> 17, "=32" -> 32, "101-150" -> 150, "101+" -> 999, null -> null */
export function rankTop(r: string | null | undefined): number | null {
  if (!r) return null;
  if (r === '101+') return 999;
  const m = r.match(/(\d+)(?:-(\d+))?/);
  return m ? Number(m[2] || m[1]) : null;
}
export function rankText(r: string | null | undefined, lang = 'en'): string {
  if (!r) return lang === 'zh' ? '未上榜' : 'not ranked';
  if (r === '101+') return lang === 'zh' ? '100 名以外' : 'below 100';
  if (r.includes('-')) return r.replace('-', '–');
  return '#' + r.replace('=', '') + (r.startsWith('=') ? (lang === 'zh' ? '（并列）' : ' (tied)') : '');
}
export function passesRank(p: { qs: string | null; us: string | null }, qsMax: number, usMax: number) {
  if (qsMax) { const v = rankTop(p.qs); if (v == null || v > qsMax) return false; }
  if (usMax) { const v = rankTop(p.us); if (v == null || v > usMax) return false; }
  return true;
}
export type Taxonomy = { dimensions: Record<Dim, { label: string; label_zh: string; description: string; description_zh: string; labels: Record<string, string>; labels_zh: Record<string, string>; labels_short: Record<string, string>; labels_short_zh: Record<string, string> }> };

export const BASE = (import.meta.env.BASE_URL as string).replace(/\/+$/, '') + '/';
export const withBase = (p: string) => BASE + p.replace(/^\/+/, '');
export const initials = (name: string) => name.split(/\s+/).filter(Boolean).filter((w) => !/^\(.*\)$/.test(w)).slice(0, 2).map((w) => w[0]).join('').toUpperCase();
export const lastName = (name: string) => { const parts = name.replace(/,.*$/, '').trim().split(/\s+/); return parts[parts.length - 1] || name; };
export function labelText(tax: Taxonomy, dim: Dim, code: string, lang: string) {
  const d = tax.dimensions[dim];
  return (lang === 'zh' ? d.labels_short_zh?.[code] : d.labels_short?.[code]) || d.labels[code] || code;
}
export function labelFull(tax: Taxonomy, dim: Dim, code: string, lang: string) {
  const d = tax.dimensions[dim];
  return (lang === 'zh' ? d.labels_zh[code] : d.labels[code]) || code;
}
export function dimLabel(tax: Taxonomy, dim: Dim, lang: string) {
  const d = tax.dimensions[dim];
  return lang === 'zh' ? d.label_zh : d.label;
}
export const RANK_ORDER: Record<string, number> = { 'Professor': 0, 'Associate Professor': 1, 'Assistant Professor': 2, 'Faculty': 3 };
export const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]!);

// an IPA-flavoured glyph for each person's main subfield, on a pastel tile (no photos are published)
const GLYPH: Record<string, string> = {
  T_PHONETICS: 'ʃ', T_PHONOLOGY: 'ŋ', T_MORPHOLOGY: '-s', T_SYNTAX: 'XP', T_SEMANTICS: 'λ', T_PRAGMATICS: '⊨',
  T_PSYCHOLING: 'ψ', T_NEUROLING: '∿', T_L1_ACQUISITION: 'ə', T_L2_BILINGUALISM: 'L2', T_APPLIED_PEDAGOGY: 'Aa',
  T_SOCIOLING: 'ɹ', T_LING_ANTHRO: 'ʔ', T_DISCOURSE_INTERACTION: '…', T_HISTORICAL: '*', T_TYPOLOGY: '∀',
  T_DOCUMENTATION: 'ɣ', T_CONTACT_CREOLES: 'θ', T_COMPUTATIONAL: '{ }', T_SIGN_GESTURE: 'ʘ', T_COGNITION_PHILOSOPHY: '∴',
};
function hash(s: string) { let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0; return Math.abs(h); }
// Person tiles were removed: they carried no information. Kept as a no-op so callers stay simple.
export function avatar(_f: Faculty, _lg = false) { return ''; }

