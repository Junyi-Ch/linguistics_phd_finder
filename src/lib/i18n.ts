export type Lang = 'en' | 'zh';
const dict: Record<string, { en: string; zh: string }> = {
  brand: { en: 'Linguistics PhD Explorer', zh: '语言学博士项目探索' },
  nav_match: { en: 'Find matches', zh: '找导师' },
  nav_programs: { en: 'Programs', zh: '项目' },
  nav_faculty: { en: 'Faculty', zh: '教师' },
  nav_shortlist: { en: 'Saved', zh: '收藏' },
  nav_about: { en: 'About', zh: '关于' },
  theme_toggle: { en: 'Toggle dark mode', zh: '切换深色模式' },
  lang_toggle: { en: '中文', zh: 'EN' },
  menu: { en: 'Menu', zh: '菜单' },
  // match page
  match_h1: { en: 'Find the linguists and programs that fit your research', zh: '找到与你研究方向契合的语言学教师与博士项目' },
  match_lede: { en: 'Paste a paragraph from your statement of purpose, or describe your questions, methods and cases. English works best; Chinese is translated on your device first. Matching runs in your browser; nothing is uploaded.', zh: '粘贴一段你的 SoP，或描述你的研究问题、方法与案例。英文效果最好；中文会先在本机翻译成英文。匹配在你的浏览器中完成，不会上传任何内容。' },
  match_placeholder: { en: 'e.g. I study how Mandarin tone is processed during spoken word recognition, using eye-tracking in the visual world paradigm with native listeners and second language learners.', zh: '例如：我研究普通话声调在口语词汇识别中如何被加工，用视觉情景范式的眼动实验比较母语者与二语学习者。' },
  match_label: { en: 'Your research interests', zh: '你的研究兴趣' },
  match_h1a: { en: 'Find the linguists and programs that fit', zh: '找到契合' },
  match_h1b: { en: 'your research', zh: '你研究方向' },
  match_h1c: { en: '', zh: '的语言学教师与博士项目' },
  match_lede2: { en: 'Describe what you want to study: your questions, methods and the languages you work on. We suggest faculty and programs whose research is closest to yours.', zh: '描述你想研究的问题、方法和语言，我们会推荐研究方向最接近的教师和项目。' },
  match_hint_title2: { en: 'We read this as', zh: '我们的理解' },
  your_query: { en: 'your query', zh: '你的描述' },
  fshort_LING: { en: 'Linguistics', zh: '语言学系' },
  fshort_COMP: { en: 'Computational', zh: '计算语言学' },
  fshort_APPLIED: { en: 'Applied / SLA', zh: '应用语言学' },
  fshort_LANG: { en: 'Language depts', zh: '语种系' },
  fshort_SPEECH: { en: 'Speech & cognition', zh: '言语与认知' },
  match_button: { en: 'Find matches', zh: '开始匹配' },
  try_example: { en: 'Try an example:', zh: '试试示例：' },
  match_loading: { en: 'Loading the matching model (first time only, about 130 MB)', zh: '正在加载匹配模型（仅首次，约 130 MB）' },
  match_running: { en: 'Finding matches', zh: '正在匹配' },
  match_translating: { en: 'Translating your text to English on your device', zh: '正在本机把你的文字翻译成英文' },
  match_rerank: { en: 'Checking the top matches', zh: '正在复核排名靠前的结果' },
  translated_note: { en: 'Matched using this English translation', zh: '按以下英文译文进行匹配' },
  translated_via_browser: { en: 'your browser’s built-in translator', zh: '浏览器内置翻译' },
  translated_via_model: { en: 'an on-device translation model', zh: '本机翻译模型' },
  translated_edit: { en: 'Edit the English and rerun', zh: '修改英文后重新匹配' },
  why_reread: { en: 'ranked higher after a closer check', zh: '复核后排名上调' },
  match_ready: { en: 'Done', zh: '完成' },
  match_hint_title: { en: 'Detected priorities', zh: '识别到的侧重' },
  match_hint_help: { en: 'Click a term to require it. Click again to ignore it.', zh: '点击某一项设为必须满足，再点一次则忽略它。' },
  match_opts: { en: 'More filters', zh: '更多筛选' },
  opt_field: { en: 'Departments', zh: '院系类型' },
  field_adjacent: { en: 'Adjacent unit', zh: '相关院系' },
  field_LING: { en: 'Linguistics departments', zh: '语言学系' },
  field_COMP: { en: 'Computational linguistics & NLP', zh: '计算语言学与 NLP' },
  field_APPLIED: { en: 'Applied linguistics & SLA', zh: '应用语言学与二语习得' },
  field_LANG: { en: 'Language-department linguistics', zh: '语种系中的语言学' },
  field_SPEECH: { en: 'Speech, hearing & cognitive science', zh: '言语听力与认知科学' },
  opt_threshold: { en: 'Minimum fit score', zh: '最低匹配分' },
  opt_lex: { en: 'Keyword weight', zh: '关键词权重' },
  opt_rank: { en: 'Rank', zh: '职称' },
  how_title: { en: 'How matching works', zh: '匹配是怎么算的' },
  how_1: { en: 'Your text is embedded on your device with an open retrieval model (Snowflake arctic-embed-m, about 110 MB, downloaded once) and compared with each faculty member’s research profile.', zh: '你的文本在本机用开源检索模型（Snowflake arctic-embed-m，约 110 MB，仅首次下载）转换成向量，与每位教师的研究画像比对。' },
  how_2: { en: 'A keyword score adds a second signal, then a small cross-encoder re-reads the top 30 against each profile. Every match shows why it was ranked.', zh: '关键词分数提供第二重信号，随后一个小型交叉编码器逐一细读前 30 名与你的描述。每条结果都会说明排名理由。' },
  how_3: { en: 'Switch to Programs to see which departments have several plausible advisors, not just one.', zh: '切换到"项目"视图，看看哪些系有不止一位可能的导师。' },
  counts: { en: '{p} programs · {f} tenure-line faculty · built {d}', zh: '{p} 个项目 · {f} 位 tenure-line 教师 · 数据构建于 {d}' },
  view_faculty: { en: 'Faculty', zh: '教师' },
  view_programs: { en: 'Programs', zh: '项目' },
  results_n: { en: '{n} matching faculty', zh: '{n} 位匹配的教师' },
  results_p: { en: '{n} programs', zh: '{n} 个项目' },
  no_results: { en: 'No close matches.', zh: '没有找到足够接近的教师。' },
  no_results_help: { en: 'Try describing your interests in more detail, lower the minimum fit score under More filters, or turn off a required term.', zh: '试着把研究兴趣写得更具体，或在“更多筛选”中降低最低匹配分，或取消“必须满足”的项。' },
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
  open_page: { en: 'Full page', zh: '完整页面' },
  research_areas: { en: 'Research areas (from the department)', zh: '研究领域（院系原文）' },
  labels_title: { en: 'Research labels', zh: '研究标签' },
  labels_note: { en: 'Labels are generated automatically from public profiles and may be incomplete. ★ marks a main focus.', zh: '标签由公开资料自动生成，可能不完整。★ 表示主要方向。' },
  sources: { en: 'Sources', zh: '来源' },
  scraped: { en: 'Directory read on', zh: '目录抓取日期' },
  report: { en: 'Report an error', zh: '报告错误' },
  confidence: { en: 'Label confidence', zh: '标签置信度' },
  // directory
  dir_h1: { en: 'Faculty', zh: '教师' },
  dir_lede: { en: 'Browse every faculty member, or narrow the list with the filters.', zh: '浏览全部教师，或用筛选缩小范围。' },
  search_ph: { en: 'Search names, schools, topics', zh: '搜索姓名、学校、研究方向' },
  all_universities: { en: 'All universities', zh: '全部学校' },
  primary_only: { en: 'Main focus only (★)', zh: '只看主要方向（★）' },
  sort: { en: 'Sort', zh: '排序' },
  sort_name: { en: 'Last name', zh: '姓氏' },
  sort_univ: { en: 'University', zh: '学校' },
  sort_rank: { en: 'Rank', zh: '职称' },
  showing: { en: 'Showing {a} of {b} faculty', zh: '显示 {a} / {b} 位教师' },
  clear: { en: 'Clear filters', zh: '清除筛选' },
  filters: { en: 'Filters', zh: '筛选' },
  // programs
  prog_h1: { en: 'Programs', zh: '博士项目' },
  prog_lede: { en: 'Pick a university on the map or in the list to see its departments and faculty.', zh: '在地图或列表中选择一所学校，查看它的院系和教师。' },
  map_view: { en: 'Map', zh: '地图' },
  list_view: { en: 'List', zh: '列表' },
  faculty_n: { en: '{n} faculty', zh: '{n} 位教师' },
  tenure_line: { en: 'Faculty', zh: '教师' },
  rank_mix: { en: '{n} ({a} professors, {b} associate, {c} assistant)', zh: '{n} 位（教授 {a}、副教授 {b}、助理教授 {c}）' },
  unit_site: { en: 'Department website', zh: '院系网站' },
  units: { en: 'Departments that grant the PhD', zh: '授予博士学位的院系' },
  phd_page: { en: 'PhD program page', zh: '博士项目页面' },
  directory_link: { en: 'Faculty directory', zh: '教师目录' },
  guide_areas: { en: 'Listed in the LSA directory as', zh: 'LSA 目录收录名称' },
  roster: { en: 'Faculty', zh: '教师' },
  rank_prof: { en: 'Professor', zh: '教授' },
  rank_assoc: { en: 'Associate Professor', zh: '副教授' },
  rank_asst: { en: 'Assistant Professor', zh: '助理教授' },
  rank_fac: { en: 'Rank not listed', zh: '职级未注明' },
  // shortlist
  sl_h1: { en: 'Saved faculty', zh: '已收藏的教师' },
  sl_lede: { en: 'Saved in this browser only. Add notes, then download your list.', zh: '只保存在当前浏览器中。可以添加备注，然后下载清单。' },
  sl_empty: { en: 'Nothing saved yet.', zh: '还没有收藏。' },
  sl_empty_help: { en: 'Click Save on any faculty member to add them here.', zh: '在任意教师旁点击“收藏”即可加入这里。' },
  sl_note: { en: 'Notes', zh: '备注' },
  sl_export_csv: { en: 'Download CSV', zh: '下载 CSV' },
  sl_export_md: { en: 'Copy list', zh: '复制清单' },
  sl_clear: { en: 'Remove all', zh: '全部移除' },
  remove: { en: 'Remove', zh: '移除' },
  copied: { en: 'Link copied', zh: '链接已复制' },
  matched_on: { en: 'Matched on', zh: '匹配依据' },
  footer_about: { en: 'How it works', zh: '工作原理' },
  footer_source: { en: 'Source code', zh: '源代码' },
  footer_by: { en: 'Made by', zh: '制作：' },
  rf_qs: { en: 'QS Linguistics rank', zh: 'QS 语言学排名' },
  rf_us: { en: 'U.S. News university rank', zh: 'U.S. News 大学综合排名' },
  rf_any: { en: 'Any', zh: '不限' },
  rf_top25: { en: 'Top 25', zh: '前 25' },
  rf_top50: { en: 'Top 50', zh: '前 50' },
  rf_top100: { en: 'Top 100', zh: '前 100' },
  rf_top200: { en: 'Top 200', zh: '前 200' },
  rf_ranked: { en: 'Ranked at all', zh: '有排名即可' },
  rankings: { en: 'Rankings', zh: '排名' },
  rank_qs_label: { en: 'QS Linguistics 2026', zh: 'QS 语言学 2026' },
  rank_us_label: { en: 'U.S. News 2027, whole university', zh: 'U.S. News 2027 大学综合' },
  rank_note: { en: 'A rough guide only: rankings say little about whether a department fits your research.', zh: '仅供粗略参考：排名很难说明一个系是否适合你的研究方向。' },
  programs_shown: { en: '{n} of {m} universities', zh: '{n} / {m} 所学校' },
  copy_link: { en: 'Share these results', zh: '分享这些结果' },
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
