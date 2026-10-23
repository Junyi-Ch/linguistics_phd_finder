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
};
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

