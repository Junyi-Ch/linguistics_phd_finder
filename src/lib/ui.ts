import { DIMS, esc, initials, avatar, labelText, labelFull, withBase, fieldLabel, type Faculty, type Program, type Taxonomy, type Dim } from './data';
import { t, getLang } from './i18n';
import * as shortlist from './shortlist';
export { avatar };

export function sig(score: number) {
  const w = Math.max(0, Math.min(100, Math.round(score * 100)));
  return `<span class="sig" aria-hidden="true"><i style="--w:${w}%"></i></span>`;
}
export function scoreHtml(score: number) {
  return `<span class="score" title="${t('fit')}">${sig(score)}<b class="num">${Math.round(score * 100)}</b></span>`;
}
export function chip(tax: Taxonomy, dim: Dim, c: string, primary = false, extra = '') {
  const lang = getLang();
  return `<span class="chip${primary ? ' primary' : ''}" data-dim="${dim}" title="${esc(labelFull(tax, dim, c, lang))}" ${extra}>${esc(labelText(tax, dim, c, lang))}${primary ? ' ★' : ''}</span>`;
}
export function saveBtn(id: string, small = true) {
  const on = shortlist.has(id);
  return `<button type="button" class="btn ${small ? 'sm' : ''} save-btn" data-save="${esc(id)}" aria-pressed="${on}">${on ? t('saved') : t('save')}</button>`;
}
export function bindSaveButtons(root: ParentNode) {
  root.querySelectorAll<HTMLButtonElement>('.save-btn').forEach((b) => {
    if (b.dataset.bound) return;
    b.dataset.bound = '1';
    b.addEventListener('click', () => {
      const on = shortlist.toggle(b.dataset.save!);
      document.querySelectorAll<HTMLButtonElement>(`.save-btn[data-save="${CSS.escape(b.dataset.save!)}"]`).forEach((x) => { x.setAttribute('aria-pressed', String(on)); x.textContent = on ? t('saved') : t('save'); });
    });
  });
}
export function personRow(f: Faculty, p: Program | undefined, tax: Taxonomy, opts: { score?: number; why?: string; chips?: Dim[]; summaryHtml?: string; maxChips?: number } = {}) {
  const lang = getLang();
  const dims = opts.chips ?? ['topic', 'approach'];
  const prim: string[] = [], rest: string[] = [];
  for (const d of dims) for (const l of f.labels[d] ?? []) (l.p ? prim : rest).push(chip(tax, d, l.c, l.p));
  const chips = [...prim, ...rest].slice(0, opts.maxChips ?? 3);
  const summary = opts.summaryHtml ?? esc(lang === 'zh' && f.summary_zh ? f.summary_zh : f.summary);
  return `<article class="row" data-id="${esc(f.id)}">
    ${avatar(f)}
    <div class="who">
      <div class="name"><button type="button" class="open-person" data-id="${esc(f.id)}">${esc(f.name)}</button></div>
      <div class="meta">${p ? `<a href="${withBase('programs/' + p.slug + '/')}">${esc(p.name)}</a> · ` : ''}${esc(f.dept)} · ${esc(f.rank === 'Faculty' ? t('rank_fac') : f.rank)}${f.fld && f.fld !== 'LING' ? ` · <span class="fld">${esc(fieldLabel(f.fld, getLang()))}</span>` : ''}</div>
      ${summary ? `<p class="sum">${summary}</p>` : ''}
      ${chips.length ? `<div class="chips">${chips.join('')}</div>` : ''}
      ${opts.why ? `<div class="why">${opts.why}</div>` : ''}
    </div>
    <div class="side">
      ${opts.score != null ? scoreHtml(opts.score) : ''}
      <div class="actions">${saveBtn(f.id)}<a class="btn sm" href="${withBase('faculty/' + f.id + '/')}">${t('details')}</a></div>
    </div>
  </article>`;
}
export function drawerHtml(f: Faculty, p: Program | undefined, tax: Taxonomy) {
  const lang = getLang();
  const focus = DIMS.flatMap((d) => (f.labels[d] ?? []).filter((l) => l.p).map((l) => chip(tax, d, l.c, false))).slice(0, 5).join('');
  const links = [
    f.site ? `<a class="btn sm" href="${esc(f.site)}" target="_blank" rel="noreferrer">${t('personal_site')}</a>` : '',
    f.profile ? `<a class="btn sm" href="${esc(f.profile)}" target="_blank" rel="noreferrer">${t('profile')}</a>` : '',
  ].join('');
  return `<button type="button" class="icon-btn close" aria-label="${t('close')}" data-close><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
  <h2>${esc(f.name)}</h2>
  <div class="muted" style="margin-top:4px">${esc(f.rank === 'Faculty' ? t('rank_fac') : f.title)}</div>
  <div style="margin-top:2px">${p ? `<a href="${withBase('programs/' + p.slug + '/')}">${esc(p.name)}</a>` : ''}<span class="muted"> · ${esc(f.dept)}</span></div>
  ${f.summary ? `<p class="sum" style="margin-top:16px;font-size:1.05rem">${esc(lang === 'zh' && f.summary_zh ? f.summary_zh : f.summary)}</p>` : ''}
  ${focus ? `<div class="chips" style="margin-top:12px">${focus}</div>` : ''}
  <div class="links" style="margin-top:18px">${saveBtn(f.id)}<a class="btn sm" href="${withBase('faculty/' + f.id + '/')}">${t('open_page')}</a>${links}</div>
  <div class="d-conn" data-for="${esc(f.id)}">
    <div class="d-tabs" role="tablist">
      <button type="button" role="tab" data-dtab="similar" aria-selected="true">${t('related_h')}</button>
      <button type="button" role="tab" data-dtab="tree" aria-selected="false">${t('tree_h')}</button>
    </div>
    <div class="d-panel" data-dpanel="similar"><p class="small muted">${t('net_loading')}</p></div>
    <div class="d-panel" data-dpanel="tree" hidden></div>
  </div>
`;
}

// network data (similar research, academic tree) for the brief view, loaded once on first use
let netPromise: Promise<any> | null = null;
function loadNet() {
  if (!netPromise) netPromise = fetch(withBase('network.json')).then((r) => r.json()).then((d) => { d.idx = new Map(d.nodes.map((n: any, i: number) => [n.id, i])); return d; }).catch((e) => { netPromise = null; throw e; });
  return netPromise;
}
function fillConnections(drawer: HTMLElement, f: Faculty) {
  const box = drawer.querySelector<HTMLElement>('.d-conn'); if (!box) return;
  const person = (n: any) => `<li><button type="button" class="link-btn open-person" data-id="${esc(n.id)}">${esc(n.n)}</button><span class="muted">${esc(n.us)}</span></li>`;
  const off = (name: string) => `<li><span class="off">${esc(name)}</span></li>`;
  loadNet().then((d) => {
    if (box.dataset.for !== f.id) return;
    const i = d.idx.get(f.id); const node = i == null ? null : d.nodes[i];
    const sim = node ? node.k.slice(0, 8).map(([j]: [number]) => person(d.nodes[j])).join('') : '';
    box.querySelector<HTMLElement>('[data-dpanel="similar"]')!.innerHTML = sim ? `<ul class="dlist">${sim}</ul>` : `<p class="small muted">—</p>`;
    const grp = (h: string, xs: any[]) => xs.length ? `<div class="d-grp"><h3>${esc(h)}</h3><ul class="dlist one">${xs.map((x) => typeof x === 'number' ? person(d.nodes[x]) : off(x)).join('')}</ul></div>` : '';
    const st = node ? node.st.slice().sort((a: any, b: any) => Number(typeof b === 'number') - Number(typeof a === 'number')) : [];
    const tree = node ? grp(t('fam_advisor'), node.av) + grp(t('tree_students'), st.slice(0, 8)) + grp(t('tree_siblings'), node.sb.map((x: any) => x[0])) : '';
    const tp = box.querySelector<HTMLElement>('[data-dpanel="tree"]')!;
    tp.innerHTML = tree ? `${tree}<p class="small" style="margin-top:12px"><a href="${withBase('faculty/' + f.id + '/#tree')}">${t('tree_full')}</a> →</p>` : `<p class="small muted">${t('fam_none')}</p>`;
  }).catch(() => { box.querySelector<HTMLElement>('[data-dpanel="similar"]')!.innerHTML = `<p class="small muted">${t('net_error')}</p>`; });
}
export function setupDrawer(getPerson: (id: string) => { f: Faculty; p?: Program } | undefined, tax: Taxonomy) {
  let backdrop = document.querySelector<HTMLElement>('.drawer-backdrop');
  let drawer = document.querySelector<HTMLElement>('.drawer');
  if (!backdrop) { backdrop = document.createElement('div'); backdrop.className = 'drawer-backdrop'; document.body.appendChild(backdrop); }
  if (!drawer) { drawer = document.createElement('aside'); drawer.className = 'drawer'; drawer.setAttribute('role', 'dialog'); drawer.setAttribute('aria-modal', 'true'); document.body.appendChild(drawer); }
  let lastFocus: HTMLElement | null = null;
  const isOpen = () => drawer!.dataset.open === 'true';
  const close = () => {
    if (!isOpen()) return;
    drawer!.dataset.open = 'false'; backdrop!.dataset.open = 'false'; document.body.style.overflow = '';
    lastFocus?.focus?.();
  };
  const open = (id: string) => {
    const x = getPerson(id); if (!x) return;
    lastFocus = document.activeElement as HTMLElement;
    drawer!.setAttribute('aria-label', x.f.name);
    drawer!.innerHTML = drawerHtml(x.f, x.p, tax);
    fillConnections(drawer!, x.f);
    drawer!.scrollTop = 0;
    drawer!.dataset.open = 'true'; backdrop!.dataset.open = 'true'; document.body.style.overflow = 'hidden';
    bindSaveButtons(drawer!);
    drawer!.querySelector<HTMLElement>('[data-close]')?.focus();
  };
  backdrop.addEventListener('click', close);
  drawer.addEventListener('click', (e) => {
    const el = e.target as HTMLElement;
    if (el.closest('[data-close]')) { close(); return; }
    const tb = el.closest<HTMLButtonElement>('[data-dtab]');
    if (tb) {
      drawer!.querySelectorAll<HTMLElement>('[data-dtab]').forEach((b) => b.setAttribute('aria-selected', String(b === tb)));
      drawer!.querySelectorAll<HTMLElement>('[data-dpanel]').forEach((p) => { p.hidden = p.dataset.dpanel !== tb.dataset.dtab; });
    }
  });
  document.addEventListener('keydown', (e) => {
    if (!isOpen()) return;
    if (e.key === 'Escape') { close(); return; }
    if (e.key === 'Tab') {
      const f = Array.from(drawer!.querySelectorAll<HTMLElement>('a[href], button:not([disabled]), textarea, input, select')).filter((el) => el.offsetParent !== null);
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  document.addEventListener('click', (e) => { const b = (e.target as HTMLElement).closest<HTMLElement>('.open-person'); if (b) open(b.dataset.id!); });
  return { open, close };
}
export function mark(text: string, terms: string[]) {
  let out = esc(text);
  const ts = terms.filter((x) => x.length > 2).sort((a, b) => b.length - a.length).slice(0, 12);
  for (const term of ts) {
    const re = new RegExp(`(^|[^\\p{L}\\p{N}])(${term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\p{L}*)`, 'giu');
    out = out.replace(re, '$1<mark>$2</mark>');
  }
  return out;
}
