import json, csv, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

P = json.load(open(sys.argv[1])); R = list(csv.DictReader(open(sys.argv[2])))
rep = {(r['slug'], r['unit']): r for r in R}

# counted by hand in a browser where the scraper failed or was clearly off: (count or None, faculty page, note)
H = {
 ("howard-university","Department of Psychology"): (15,"https://psychology.howard.edu/faculty-staff",""),
 ("lehigh-university","Department of Psychology"): (17,"https://psychology.cas.lehigh.edu/faculty-staff",""),
 ("michigan-state-university","Department of Psychology"): (None,"https://psychology.msu.edu/people","directory is drawn by script; not counted"),
 ("michigan-state-university","Neuroscience Program"): (76,"https://directory.natsci.msu.edu/Directory/Directory/Department/31","count from the first scraper run"),
 ("purdue-university-main-campus","Department of Psychological Sciences"): (23,"https://hhs.purdue.edu/about-hhs/directory/?staff_faculty_type=Faculty&hhs_department_staff=Department%20of%20Psychological%20Sciences",""),
 ("texas-aandm-university","Texas A&M Institute for Neuroscience"): (20,"https://tamin.tamu.edu/research/affiliated-faculty/","people listed; page gives no titles"),
 ("the-ohio-state-university","Neuroscience Graduate Program"): (99,"https://ngp.osu.edu/people",""),
 ("university-of-california-irvine","Department of Psychological Science"): (None,"https://ps.soceco.uci.edu/faculty","site did not load; recheck"),
 ("university-of-california-merced","Department of Psychological Sciences"): (22,"https://psychology.ucmerced.edu/faculty",""),
 ("university-of-california-merced","Department of Cognitive and Information Sciences"): (13,"https://cogsci.ucmerced.edu/faculty",""),
 ("university-of-california-riverside","Department of Psychological and Brain Sciences"): (35,"https://profiles.ucr.edu/app/embed?groupId=70644&affiliationFilter=Faculty&viewProfilesMode=cards",""),
 ("university-of-california-riverside","Neuroscience Graduate Program"): (54,"https://profiles.ucr.edu/app/embed?groupId=110928&viewProfilesMode=cards",""),
 ("university-of-illinois-chicago","Department of Psychology"): (26,"https://psch.uic.edu/people/faculty/",""),
 ("university-of-miami","Department of Psychology"): (50,"https://www.psy.miami.edu/people/faculty/index.html","mostly clinical and health psychology"),
 ("university-of-michigan-ann-arbor","Neuroscience Graduate Program"): (150,"https://medschool.umich.edu/interdisciplinary-programs/neuroscience-graduate-program/faculty","program's own figure: 150+ core and affiliated"),
 ("university-of-pittsburgh","Department of Psychology"): (31,"https://www.psychology.pitt.edu/people","core faculty; the page also lists ~45 secondary appointments"),
 ("virginia-tech","Department of Psychology"): (35,"https://support.psyc.vt.edu/users",""),
 ("virginia-tech","School of Neuroscience"): (15,"https://neuroscience.vt.edu/our-people.html","research faculty"),
 ("carnegie-mellon-university","Department of Psychology"): (22,"https://www.cmu.edu/dietrich/psychology/directory/index.html",""),
 ("pennsylvania-state-university-university-park","Department of Psychology"): (41,"https://psych.la.psu.edu/research/faculty-research-interests/",""),
 ("washington-university-in-st-louis","Department of Psychological and Brain Sciences"): (56,"https://psych.washu.edu/people?cat=88","two pages"),
 ("northeastern-university","Department of Psychology"): (None,"https://cos.northeastern.edu/people/?department=psychology","list mixes faculty and students over several pages; not counted"),
 ("florida-international-university","Department of Psychology"): (None,"https://case.fiu.edu/about/directory/index.html","college directory; not counted"),
 ("emory-university","Neuroscience PhD (Laney Graduate School)"): (None,"https://biomed.emory.edu/PROGRAM_SITES/NS/about-us/faculty-search.html","search tool, no list; not counted"),
 ("university-of-california-san-diego","Department of Psychology"): (27,"https://catalog.ucsd.edu/faculty/PSYC.html","from the course catalog"),
 ("stony-brook-university-suny","Department of Psychology"): (33,"https://www.stonybrook.edu/psychology/people/faculty.html","13 of them clinical"),
 ("university-of-texas-austin","Interdisciplinary Neuroscience Program"): (40,"https://inp.neuroscience.utexas.edu/faculty-directory","approximate: the PhD is the Interdisciplinary Neuroscience Program, ~10 per page over 4 pages"),
 ("university-of-illinois-chicago","Graduate Program in Neuroscience"): (None,"https://gpn.uic.edu/people/faculty/","listed A–Z on separate pages; not counted"),
 ("yale-university","Interdepartmental Neuroscience Program"): (22,"https://medicine.yale.edu/inp/people/","first 22 shown; full list is longer"),
 ("cornell-university","Department of Psychology (College of Human Ecology; formerly Human Development)"): (22,"https://human.cornell.edu/people?department%5B0%5D=33&role%5B0%5D=24",""),
 ("rochester-institute-of-technology","School of Psychology and Cognitive Science"): (None,"https://www.rit.edu/liberalarts/school-psychology-and-cognitive-science","site refused the browser; earlier count was college-wide"),
 ("dartmouth-college","Department of Psychological and Brain Sciences"): (25,"https://pbs.dartmouth.edu/people","may undercount: many cards have no titles"),
}
# my call after looking: left out
OUT = {}

TYPE = {"PSY":"Psychology","COGSCI":"Cognitive science","NEURO":"Neuroscience"}
HOME = {"main":"Main campus","mixed":"Main campus + medical school","med":"Medical school"}

rows = []
for p in P:
    if not p["units"]:
        rows.append([p["rank_usnews_national"], p["university"], "—", "", "", "Left out", "no psychology, cognitive science or neuroscience PhD", None, "", "", ""])
        continue
    for u in p["units"]:
        key = (p["slug"], u["name"]); r = rep.get(key)
        inc = u["include"] and key not in OUT
        if not inc:
            decision, why = "Left out", OUT.get(key) or u["note"]
        elif u.get("filter_psych"):
            decision, why = "Included (psych-relevant people only)", "mixed program: keep people whose research is relevant to psychology"
        else:
            decision, why = "Included", u["note"]
        count, link, src, cnote = None, u.get("directory_url") or u["unit_url"], "", ""
        if key in H:
            count, link, cnote = H[key]; src = "counted by hand" if count is not None else "not counted"
        elif r and inc:
            count = int(r["tenure_line"] or 0); link = r["directory"] or link; src = "scraper"
            if r["status"] == "CHECK": src, cnote = "scraper (low, check)", r["note"].strip()
        if not inc and not r and key not in H: src = ""
        rows.append([p["rank_usnews_national"], p["university"], u["name"], TYPE[u["field"]], HOME[u["home"]], decision, why, count, src, link, cnote])

wb = Workbook(); ws = wb.active; ws.title = "Inventory"
hdr = ["US News rank","University","Unit","Type","Where it sits","Decision","Why","Tenure-line faculty (approx.)","How counted","Faculty list","Count note"]
ws.append(hdr)
for r in rows: ws.append(r)
F = Font(name="Arial", size=10); B = Font(name="Arial", size=10, bold=True, color="FFFFFF")
for row in ws.iter_rows():
    for c in row: c.font = F; c.alignment = Alignment(vertical="top", wrap_text=c.column in (3,7,11))
for c in ws[1]: c.font = B; c.fill = PatternFill("solid", fgColor="16151F"); c.alignment = Alignment(wrap_text=True, vertical="center")
for i in range(2, ws.max_row+1):
    c = ws.cell(i, 10)
    if c.value: c.hyperlink = c.value; c.font = Font(name="Arial", size=10, color="4A2FB8", underline="single")
    d = ws.cell(i, 6).value
    ws.cell(i, 6).fill = PatternFill("solid", fgColor={"Included":"E8F5E9","Left out":"F3F3F3"}.get(d, "FFF6E0"))
widths = [8,30,40,15,22,30,48,14,18,50,40]
for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "C2"
n = ws.max_row
t = Table(displayName="Units", ref=f"A1:K{n}"); t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True); ws.add_table(t)

# Summary per university, with formulas over the Inventory sheet
s = wb.create_sheet("By university")
s.append(["US News rank","University","Units included","Psychology + cog sci faculty (included)","Neuroscience faculty (included, before psych filter)","Units not counted"])
seen = []
for r in rows:
    if r[1] not in [x[1] for x in seen]: seen.append((r[0], r[1]))
for i,(rk,name) in enumerate(seen, start=2):
    q = f'"{name}"'.replace("'", "''")
    s.append([rk, name,
      f'=COUNTIFS(Inventory!$B$2:$B${n},B{i},Inventory!$F$2:$F${n},"Included*")',
      f'=SUMIFS(Inventory!$H$2:$H${n},Inventory!$B$2:$B${n},B{i},Inventory!$F$2:$F${n},"Included*",Inventory!$D$2:$D${n},"Psychology")+SUMIFS(Inventory!$H$2:$H${n},Inventory!$B$2:$B${n},B{i},Inventory!$F$2:$F${n},"Included*",Inventory!$D$2:$D${n},"Cognitive science")',
      f'=SUMIFS(Inventory!$H$2:$H${n},Inventory!$B$2:$B${n},B{i},Inventory!$F$2:$F${n},"Included*",Inventory!$D$2:$D${n},"Neuroscience")',
      f'=COUNTIFS(Inventory!$B$2:$B${n},B{i},Inventory!$F$2:$F${n},"Included*",Inventory!$I$2:$I${n},"not counted")'])
m = s.max_row
s.append([]); s.append(["","Total", f"=SUM(C2:C{m})", f"=SUM(D2:D{m})", f"=SUM(E2:E{m})", f"=SUM(F2:F{m})"])
s.append(["","Universities with at least one included unit", f'=COUNTIF(C2:C{m},">0")'])
s.append(["","Note: neuroscience programs overlap heavily with psychology departments and include medical-school faculty, so the neuroscience column is an upper bound before the psych-relevance filter; totals are not unique people."])
for row in s.iter_rows():
    for c in row: c.font = F
for c in s[1]: c.font = B; c.fill = PatternFill("solid", fgColor="16151F"); c.alignment = Alignment(wrap_text=True, vertical="center")
for r in (m+2, m+3): 
    for c in s[r]: c.font = Font(name="Arial", size=10, bold=True)
for i,w in enumerate([8,42,12,20,24,12],1): s.column_dimensions[get_column_letter(i)].width = w
s.freeze_panes = "C2"

nt = wb.create_sheet("Read me")
notes = [
 ["Psychology PhD Explorer — department inventory"],
 [""],
 ["Scope","U.S. News 2027 Best National Universities, top 100 (108 schools with the ties at #100)."],
 ["Source","https://poetsandquantsforundergrads.com/news/u-s-news-best-colleges-ranking-2027-mit-ends-princetons-long-run-at-the-top/2/"],
 ["Included","Psychology departments and their equivalents (e.g. Psychological & Brain Sciences, MIT Brain & Cognitive Sciences), cognitive science departments, and departments or programs named neuroscience."],
 ["Left out","Neurobiology departments; neuroscience programs run from a medical school; clinical psychology units; education-school psychology; schools without a research PhD in these fields."],
 ["Mixed programs","Neuroscience programs with both main-campus and medical-school faculty are included, but only people whose research is relevant to psychology will be kept when the site is built."],
 ["Clinical faculty","Counts inside psychology departments still include clinical-area faculty; they are dropped later, when profiles are labelled."],
 ["Counts","Approximate tenure-line faculty (assistant, associate and full professors) from each unit's faculty page, found by pipeline/scrape_local.py --dir-only on 24 Oct 2026, or counted by hand in a browser where the scraper failed (column 'How counted'). Blank = not counted, with the reason in 'Count note'."],
 ["Overlap","Many people appear in both a psychology department and a neuroscience program; totals are not unique people."],
]
for r in notes: nt.append(r)
nt["A1"].font = Font(name="Arial", size=13, bold=True)
for row in nt.iter_rows(min_row=3):
    row[0].font = Font(name="Arial", size=10, bold=True)
    if len(row) > 1: row[1].font = F; row[1].alignment = Alignment(wrap_text=True, vertical="top")
nt.column_dimensions["A"].width = 16; nt.column_dimensions["B"].width = 110
wb.move_sheet("Read me", offset=-2)
wb.save(sys.argv[3])
print(len(rows), "rows")
