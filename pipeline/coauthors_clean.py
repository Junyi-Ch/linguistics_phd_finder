"""Second pass after coauthors.py: drop OpenAlex profiles whose papers belong to a different person
(mostly papers in another science and little that fits the person's research), then rebuild pairs.
Run from the repo root: python3 pipeline/coauthors_clean.py"""
import json, glob, re, collections, hashlib, sys
C='data/cache/openalex'
src=json.load(open('src/data/coauthors.json'))
RAW='data/cache/coauthors_raw.json'   # the uncleaned output of coauthors.py, so this step can be rerun
if src.get('cleaned'): src=json.load(open(RAW))
else: json.dump(src,open(RAW,'w'))
F={f['id']:f for f in json.load(open('src/data/faculty.json'))}
LANG=re.compile(r"lingu|language|speech|phon|word|lexic|syntax|syntac|semantic|pragmatic|discourse|grammar|morpholog|sentence|verb|noun|reading|bilingual|dialect|accent|vowel|consonant|tone|prosod|sign|gesture|translation|corpus|parsing|parser|nlp|text|dialog|vocabul|literacy|writing|spoken|spelling|meaning|pronoun|clause|tense|aspect|quantif|acquisition|learner|esl|efl|l2|second|heritage|endangered|documentation|creole|pidgin|sociolinguist|narrative|conversation|communicat|aphasia|stutter|voice|hearing|auditory|perception|cognit|brain|neural|model|infant|child|student|teacher|classroom|instruction|education|culture|indigenous|ethnograph|identity|mandarin|chinese|spanish|english|japanese|korean|arabic|german|french|russian|portuguese|italian|hindi|bantu|mayan|quechua|tagalog|turkish", re.I)
STOP=set("about after again also among another based because before being between both cases could does doing during each early first from further have having into itself just language languages linguistic linguistics more most other over same should since some such than that their them then there these they this those through under until very what when where which while with within would study studies studying research using uses focus focuses including especially department professor university".split())
def vocab(f):
    text=' '.join([f.get('summary') or '', ' '.join(f.get('areas') or []), ' '.join(f.get('kw') or []), f.get('dept') or ''])
    return {w for w in re.findall(r"[a-zà-ÿ]{5,}", text.lower()) if w not in STOP}
def fits(title, voc):
    t=title.lower()
    return bool(LANG.search(title)) or any(w in t for w in voc)
SCI=re.compile(r"\b(cells?|cellular|protein|genes?|genom|cancer|tumou?r|patients?|clinical|therap|disease|mouse|mice|rats?\b|receptor|kinase|inhibitor|synthes|catalys|catalyt|graphene|semiconduct|nanorib|proton|nuclei|nuclear|stellar|laser|volcan|magma|pyroclast|tecton|birds?|avian|species|plants?|fruits?|fung|bacteri|virus|viral|infect|hepat|surg|bone|imaging|radiolog|osteo|diet|exercise|obes|weight loss|metabol|lognormal|polymer|alloy|ecolog|nutrition|hiv|drugs?|pharmac|bioactiv|chemical|compound|voltage|circuit|phosphat|staphylococ|antibod|mastectom|retinopath|diabet|cardi|stroke|carbon|oxidation|crystal|magnetic|spin|quantum|galax|enzym|tissue|molecul|lipid|insulin|vaccin|epidem|wildlife|soil|marine|seed)", re.I)
keep, report = {}, []
works_by = {}
for fid, ids in src['authors'].items():
    key=hashlib.md5('|'.join(ids).encode()).hexdigest()[:8]
    ws=[]
    for fn in sorted(glob.glob(f'{C}/works-{fid}-{key}-*.json')): ws+=json.load(open(fn)).get('results',[])
    works_by[fid]=ws
    voc=vocab(F[fid])
    per=collections.defaultdict(lambda:[0,0])
    for w in ws:
        mine={((a.get('author') or {}).get('id') or '').rsplit('/',1)[-1] for a in (w.get('authorships') or [])} & set(ids)
        for a in mine:
            per[a][0]+=1; per[a][1]+=fits(w.get('title') or '', voc)
    sci=collections.defaultdict(int)
    for w in ws:
        mine={((a.get('author') or {}).get('id') or '').rsplit('/',1)[-1] for a in (w.get('authorships') or [])} & set(ids)
        if SCI.search(w.get('title') or ''):
            for a in mine: sci[a]+=1
    def ok(a):
        n,fit=per[a]
        if n==0: return False
        if n>=5 and sci[a]/n>=0.25 and fit/n<0.35: return False      # mostly papers in another science: a different person
        if n>=10 and fit/n<0.08: return False          # almost nothing that fits their research
        if n<5 and fit==0 and sci[a]>0: return False
        return True
    good=[a for a in ids if ok(a)]
    dropped=[(a,per[a][0],round(per[a][1]/per[a][0],2) if per[a][0] else None, round(sci[a]/per[a][0],2) if per[a][0] else None) for a in ids if a not in good]
    if dropped: report.append((fid, good, dropped))
    if good: keep[fid]=good
print('faculty kept',len(keep),'of',len(src['authors']),'; faculty with a profile dropped:',len(report))
for fid,good,dropped in report:
    print(f"  {F[fid]['name'][:26]:26} kept {len(good)} dropped {dropped}")
# rebuild pairs from kept profiles only
owner={a:fid for fid,ids in keep.items() for a in ids}
pairs={}
for fid, ids in keep.items():
    for w in works_by[fid]:
        au=w.get('authorships') or []
        if len(au)>25: continue
        ids_here={((a.get('author') or {}).get('id') or '').rsplit('/',1)[-1] for a in au}
        if not ids_here & set(ids): continue
        for o in {owner.get(x) for x in ids_here} - {None, fid}:
            a,b=sorted((fid,o)); e=pairs.setdefault((a,b),{'w':set(),'y':0,'t':''})
            if w['id'] in e['w']: continue
            e['w'].add(w['id']); y=w.get('publication_year') or 0
            if y>=e['y']: e['y'],e['t']=y,(w.get('title') or '')[:200]
out=dict(src); out['authors']=keep; out['matched']=len(keep)
out['pairs']=sorted([[a,b,len(e['w']),e['y'],e['t']] for (a,b),e in pairs.items()], key=lambda r:(-r[2],r[0]))
out['checked']='profiles whose publication titles do not fit the person’s research description were removed'
out['cleaned']=True
json.dump(out,open('src/data/coauthors.json','w'),ensure_ascii=False,separators=(',',':'))
print('pairs before',len(src['pairs']),'after',len(out['pairs']))
