# Running the data pipeline on a Mac

Everything here runs on your own computer: free, and nothing goes through Claude. Open **Terminal** and paste one block at a time.

## Once: set up

```bash
cd ~/Desktop/linguistics_phd
python3 --version                      # needs 3.9 or newer; if macOS offers to install developer tools, accept
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r pipeline/requirements.txt
python -m playwright install chromium
```

For the labels, install **Ollama** from https://ollama.com/download (open the app once), then:

```bash
ollama pull qwen2.5:7b
```

Each later Terminal session starts with `cd ~/Desktop/linguistics_phd && source .venv/bin/activate`.

## 1. Find the faculty pages (about 10 minutes)

```bash
python pipeline/scrape_local.py --dir-only
```

This finds each department's faculty page and counts tenure-line professors, without reading profiles yet. It ends with a list of units marked **CHECK** in `data/cache/scrape_report.csv`. Tell Claude when it finishes; Claude reads that report and fixes the program list.

## 2. Read the profiles (about 1 hour)

```bash
python pipeline/scrape_local.py
python pipeline/validate_raw.py data/raw/*.json
```

## 3. Add recent publications from OpenAlex (about 15 minutes, optional)

```bash
python pipeline/enrich_openalex.py
```

## 4. Write summaries and labels with the local model (a few hours; can run overnight)

Keep the Mac plugged in and awake (System Settings → Battery → prevent sleeping, or run `caffeinate -i` in front of the command):

```bash
caffeinate -i python pipeline/label_local.py
python pipeline/validate_labels.py data/labels/*.json
```

If it stops, run the same command again: it continues where it left off.

## 5. Build the matching data and preview the site

```bash
python pipeline/build.py
python pipeline/report.py
npm install
npm run dev
```

Open http://localhost:4321/linguistics_phd_finder/ to try it.

## 6. Publish

```bash
git add -A
git commit -m "Add faculty data"
git push -u origin main
```

Then on GitHub: the repo → Settings → Pages → Source: **GitHub Actions**. The site appears at https://junyi-ch.github.io/linguistics_phd_finder/ a few minutes after each push.
