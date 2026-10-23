export type Lang = 'en' | 'zh';
const dict: Record<string, { en: string; zh: string }> = {
  brand: { en: 'Linguistics PhD Explorer', zh: '语言学博士项目探索' },
  nav_match: { en: 'Match', zh: '匹配' },
  nav_programs: { en: 'Programs', zh: '项目' },
  nav_faculty: { en: 'Faculty', zh: '教师' },
  nav_shortlist: { en: 'Shortlist', zh: '清单' },
  nav_about: { en: 'About', zh: '关于' },
  theme_toggle: { en: 'Toggle dark mode', zh: '切换深色模式' },
  lang_toggle: { en: '中文', zh: 'EN' },
  menu: { en: 'Menu', zh: '菜单' },
  // match page
  match_h1: { en: 'Find the linguists and programs that fit your research', zh: '找到与你研究方向契合的语言学教师与博士项目' },
  match_lede: { en: 'Paste a paragraph from your statement of purpose, or describe your questions, methods and cases. English works best; Chinese is translated on your device first. Matching runs in your browser; nothing is uploaded.', zh: '粘贴一段你的 SoP，或描述你的研究问题、方法与案例。英文效果最好；中文会先在本机翻译成英文。匹配在你的浏览器中完成，不会上传任何内容。' },
  match_placeholder: { en: 'Example: I study how Mandarin tone is processed during spoken word recognition, using eye-tracking in the visual world paradigm with native listeners and second language learners. I am also interested in computational models of speech perception.', zh: '示例：我研究普通话声调在口语词汇识别中如何被加工，用视觉情景范式的眼动实验比较母语者与二语学习者，也关注言语感知的计算模型。' },
  match_label: { en: 'Your research interests', zh: '你的研究兴趣' },
  match_h1a: { en: 'Find the linguists and programs that fit', zh: '找到契合' },
  match_h1b: { en: 'your research', zh: '你研究方向' },
  match_h1c: { en: '', zh: '的语言学教师与博士项目' },
  match_lede2: { en: 'Describe what you want to study. We read it for subfield, method, data and language, and match it with faculty in US linguistics PhD programs and the departments around them. Matching runs in your browser; nothing is uploaded.', zh: '描述你想研究的内容。我们会从研究领域、方法、数据和语言几个方面理解它，并与美国语言学博士项目及相关院系的教师进行匹配。匹配在你的浏览器中完成，不会上传任何内容。' },
  match_hint_title2: { en: 'We read this as', zh: '我们的理解' },
  your_query: { en: 'your query', zh: '你的描述' },
  fshort_LING: { en: 'Linguistics', zh: '语言学系' },
  fshort_COMP: { en: 'Computational', zh: '计算语言学' },
  fshort_APPLIED: { en: 'Applied / SLA', zh: '应用语言学' },
  fshort_LANG: { en: 'Language depts', zh: '语种系' },
  fshort_SPEECH: { en: 'Speech & cognition', zh: '言语与认知' },
  match_button: { en: 'Find matches', zh: '开始匹配' },
  try_example: { en: 'Try an example:', zh: '试试示例：' },
  match_loading: { en: 'Downloading the language models (once, about 130 MB)', zh: '正在下载语言模型（仅首次，约 130 MB）' },
  match_running: { en: 'Scoring faculty', zh: '正在计算匹配度' },
  match_translating: { en: 'Translating your text to English on your device', zh: '正在本机把你的文字翻译成英文' },
  match_rerank: { en: 'Re-reading the top matches', zh: '正在细读排名靠前的结果' },
  translated_note: { en: 'Matched using this English translation', zh: '按以下英文译文进行匹配' },
  translated_via_browser: { en: 'your browser’s built-in translator', zh: '浏览器内置翻译' },
  translated_via_model: { en: 'an on-device translation model', zh: '本机翻译模型' },
  translated_edit: { en: 'Edit the English and rerun', zh: '修改英文后重新匹配' },
  why_reread: { en: 'moved up on re-reading', zh: '细读后上调' },
  match_ready: { en: 'Model ready', zh: '模型已就绪' },
  match_hint_title: { en: 'Detected priorities', zh: '识别到的侧重' },
  match_hint_help: { en: 'Click a chip to boost it; click again to require it.', zh: '点一下加权，再点一下变为必须满足。' },
  match_opts: { en: 'Options', zh: '选项' },
  opt_field: { en: 'Units', zh: '院系类型' },
  field_adjacent: { en: 'Adjacent unit', zh: '相关院系' },
  field_LING: { en: 'Linguistics departments', zh: '语言学系' },
  field_COMP: { en: 'Computational linguistics & NLP', zh: '计算语言学与 NLP' },
  field_APPLIED: { en: 'Applied linguistics & SLA', zh: '应用语言学与二语习得' },
  field_LANG: { en: 'Language-department linguistics', zh: '语种系中的语言学' },
  field_SPEECH: { en: 'Speech, hearing & cognitive science', zh: '言语听力与认知科学' },
  opt_threshold: { en: 'Minimum fit', zh: '最低匹配度' },
  opt_lex: { en: 'Keyword weight', zh: '关键词权重' },
  opt_rank: { en: 'Rank', zh: '职称' },
  how_title: { en: 'How matching works', zh: '匹配是怎么算的' },
  how_1: { en: 'Your text is embedded on your device with an open retrieval model (Snowflake arctic-embed-m, about 110 MB, downloaded once) and compared with each faculty member’s research profile.', zh: '你的文本在本机用开源检索模型（Snowflake arctic-embed-m，约 110 MB，仅首次下载）转换成向量，与每位教师的研究画像比对。' },
  how_2: { en: 'A keyword score adds a second signal, then a small cross-encoder re-reads the top 30 against each profile. Every match shows why it was ranked.', zh: '关键词分数提供第二重信号，随后一个小型交叉编码器逐一细读前 30 名与你的描述。每条结果都会说明排名理由。' },
  how_3: { en: 'Switch to Programs to see which departments have several plausible advisors, not just one.', zh: '切换到"项目"视图，看看哪些系有不止一位可能的导师。' },
  counts: { en: '{p} programs · {f} tenure-line faculty · built {d}', zh: '{p} 个项目 · {f} 位 tenure-line 教师 · 数据构建于 {d}' },
  view_faculty: { en: 'Faculty', zh: '教师' },
  view_programs: { en: 'Programs', zh: '项目' },
  results_n: { en: '{n} faculty at or above the minimum fit', zh: '{n} 位教师达到最低匹配度' },
  results_p: { en: '{n} programs with at least one match', zh: '{n} 个项目至少有一位匹配教师' },
  no_results: { en: 'No faculty reached the minimum fit.', zh: '没有教师达到最低匹配度。' },
  no_results_help: { en: 'Lower the minimum fit, remove a required chip, or describe your work more concretely.', zh: '试试降低最低匹配度、取消"必须满足"的标签，或把研究描述写得更具体。' },
  load_more: { en: 'Show {n} more', zh: '再显示 {n} 条' },
  why: { en: 'Why', zh: '原因' },
  why_sem: { en: 'semantic', zh: '语义' },
  why_kw: { en: 'keyword overlap', zh: '关键词重合' },
  why_labels: { en: 'shares your priorities', zh: '符合你的侧重' },
  fit: { en: 'Fit', zh: '匹配度' },
  matches: { en: 'matches', zh: '位匹配' },
  top_matches: { en: 'Strongest matches', zh: '最匹配的教师' },
  cjk_notice: { en: 'Chinese text is translated to English on your device before matching (the browser’s own translator when available, otherwise a one-time 110 MB model). The translation is shown with the results so you can correct it.', zh: '中文会先在本机翻译成英文再匹配（优先使用浏览器内置翻译，否则一次性下载约 110 MB 的翻译模型）。译文会和结果一起显示，方便你修改。' },
  model_error: { en: 'The model could not be downloaded. Check your connection, or try again; a mirror is used automatically when huggingface.co is unreachable.', zh: '模型下载失败。请检查网络后重试；当 huggingface.co 不可用时会自动切换镜像。' },
  // shared
  save: { en: 'Save', zh: '收藏' },
  saved: { en: 'Saved', zh: '已收藏' },
  details: { en: 'Details', zh: '详情' },
  profile: { en: 'Department profile', zh: '院系主页' },
  personal_site: { en: 'Personal site', zh: '个人网站' },
  scholar: { en: 'Google Scholar', zh: 'Google Scholar' },
  close: { en: 'Close', zh: '关闭' },
  open_page: { en: 'Open full page', zh: '打开完整页面' },
  research_areas: { en: 'Research areas (as listed by the department)', zh: '研究领域（院系原文）' },
  labels_title: { en: 'Research labels', zh: '研究标签' },
  labels_note: { en: 'Labels are generated from public profiles and are interpretive aids, not a complete account of anyone’s work. ★ marks a primary emphasis.', zh: '标签由公开资料自动生成，仅作解释性参考，不代表完整学术画像。★ 为主要侧重。' },
  sources: { en: 'Sources', zh: '来源' },
  scraped: { en: 'Directory read on', zh: '目录抓取日期' },
  report: { en: 'Report an error', zh: '报告错误' },
  confidence: { en: 'Label confidence', zh: '标签置信度' },
  // directory
  dir_h1: { en: 'Faculty directory', zh: '教师目录' },
  dir_lede: { en: 'Every tenure-line faculty member in the collected programs, by subfield, method, data, population and language. Filters combine; counts update as you narrow.', zh: '收录项目中的全部 tenure-line 教师，按研究领域、方法、数据、人群与语言五个维度浏览。筛选可叠加，计数随之更新。' },
  search_ph: { en: 'Search name, school, subfield or language', zh: '搜索姓名、学校、领域或语言' },
  all_universities: { en: 'All universities', zh: '全部学校' },
  primary_only: { en: 'Primary labels only', zh: '只看主要侧重' },
  sort: { en: 'Sort', zh: '排序' },
  sort_name: { en: 'Last name', zh: '姓氏' },
  sort_univ: { en: 'University', zh: '学校' },
  sort_rank: { en: 'Rank', zh: '职称' },
  showing: { en: 'Showing {a} of {b} faculty', zh: '显示 {a} / {b} 位教师' },
  clear: { en: 'Clear filters', zh: '清除筛选' },
  filters: { en: 'Filters', zh: '筛选' },
  // programs
  prog_h1: { en: 'Programs', zh: '博士项目' },
  prog_lede: { en: 'Linguistics doctoral programs and the units around them, on the map or as a list. Pick one to see its units, links and complete faculty roster.', zh: '美国语言学博士项目及相关院系，地图或列表浏览。点击查看院系、链接与完整教师名册。' },
  map_view: { en: 'Map', zh: '地图' },
  list_view: { en: 'List', zh: '列表' },
  faculty_n: { en: '{n} faculty', zh: '{n} 位教师' },
  tenure_line: { en: 'Tenure-line faculty', zh: 'Tenure-line 教师' },
  rank_mix: { en: '{n} — {a} professors · {b} associate · {c} assistant', zh: '{n} 位 — 教授 {a} · 副教授 {b} · 助理教授 {c}' },
  unit_site: { en: 'Unit website', zh: '院系网站' },
  units: { en: 'Units granting the PhD', zh: '授予博士学位的院系' },
  phd_page: { en: 'PhD program page', zh: '博士项目页面' },
  directory_link: { en: 'Faculty directory', zh: '教师目录' },
  guide_areas: { en: 'Listed in the LSA directory as', zh: 'LSA 目录收录名称' },
  roster: { en: 'Faculty roster', zh: '教师名册' },
  rank_prof: { en: 'Professor', zh: '教授' },
  rank_assoc: { en: 'Associate Professor', zh: '副教授' },
  rank_asst: { en: 'Assistant Professor', zh: '助理教授' },
  rank_fac: { en: 'Rank not listed', zh: '职级未注明' },
  // shortlist
  sl_h1: { en: 'Shortlist', zh: '申请清单' },
  sl_lede: { en: 'Faculty you saved, kept in this browser only. Add notes, then export to your application tracker.', zh: '你收藏的教师，仅保存在本浏览器。可添加备注，再导出到申请追踪表。' },
  sl_empty: { en: 'Nothing saved yet.', zh: '还没有收藏。' },
  sl_empty_help: { en: 'Use Save on any faculty card or page.', zh: '在任意教师卡片或页面点击"收藏"。' },
  sl_note: { en: 'Notes', zh: '备注' },
  sl_export_csv: { en: 'Export CSV', zh: '导出 CSV' },
  sl_export_md: { en: 'Copy as Markdown', zh: '复制为 Markdown' },
  sl_clear: { en: 'Remove all', zh: '清空' },
  remove: { en: 'Remove', zh: '移除' },
  copied: { en: 'Copied', zh: '已复制' },
  copy_link: { en: 'Copy link', zh: '复制链接' },
};

export function getLang(): Lang {
  if (typeof document === 'undefined') return 'en';
  const l = document.documentElement.lang;
  return l === 'zh' ? 'zh' : 'en';
}
export function t(key: string, vars?: Record<string, string | number>): string {
  const e = dict[key];
  let s = e ? e[getLang()] : key;
  if (vars) for (const k of Object.keys(vars)) s = s.replace(new RegExp(`\\{${k}\\}`, 'g'), String(vars[k]));
  return s;
}
export function applyI18n(root: ParentNode = document) {
  root.querySelectorAll<HTMLElement>('[data-i18n]').forEach((el) => {
    const key = el.dataset.i18n!;
    const attr = el.dataset.i18nAttr;
    const v = t(key);
    if (attr) el.setAttribute(attr, v); else el.textContent = v;
  });
}
export function setLang(l: Lang) {
  document.documentElement.lang = l;
  try { localStorage.setItem('lang', l); } catch {}
  applyI18n();
  document.dispatchEvent(new CustomEvent('langchange', { detail: l }));
}
export function initLang() {
  let l: Lang = 'en';
  try { const s = localStorage.getItem('lang'); if (s === 'zh') l = 'zh'; } catch {}
  document.documentElement.lang = l;
  applyI18n();
}
