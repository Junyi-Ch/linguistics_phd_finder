# Pages saved by hand

Some sites (UCLA, Harvard) block automated browsers. Open the faculty page in your normal browser, choose
File → Save Page As… → "Web Page, HTML Only", and save it here with the name the unit's `saved_pages`
pattern in data/programs.json expects (e.g. `ucla-1.html`, `ucla-2.html` for each page of the list).
The scraper then reads names, titles and research interests from these files (`cards_only`: profiles are not fetched).
