# H2O Engineering Group website

Website of the Hydro Hazards and Ocean Engineering (H2O) Group, Department of Civil
Engineering, IIT Bombay. It is a plain static site (HTML + CSS, no build step needed)
for GitHub Pages. Content was copied from the original Google Site
(https://sites.google.com/view/h2o-engineering-lab).

## Structure

```
index.html                      Home
about-ananth/ (education, experience; bio/ only forwards to about-ananth/)
current-members/
research/ (8 project pages + miscellaneous; research-overview/ only forwards to research/)
publications/   projects/   news-and-updates/   contact/
assets/css/style.css            all styling (colours at the top)
assets/img/                     all images
assets/js/site.js               menu, scroll animations, photo viewer (lightbox), gallery
tools/build_site.py             generator used to create the pages (optional)
tools/content.json              text extracted from the Google Site
tools/google_site_backup/       full HTML backup of the original Google Site pages
```

## Publish on GitHub Pages

1. Create a new **public** repository on GitHub, e.g. `h2o-engineering-lab`
   (or `<username>.github.io` for a root URL).
2. Upload everything in this folder (Add file → Upload files, drag the folder contents),
   or with git:
   ```
   git init
   git add .
   git commit -m "H2O Engineering Lab website"
   git branch -M main
   git remote add origin https://github.com/<username>/h2o-engineering-lab.git
   git push -u origin main
   ```
3. Repository → Settings → Pages → Source: *Deploy from a branch*, Branch: `main`, folder `/ (root)` → Save.
4. After a minute the site is live at `https://<username>.github.io/h2o-engineering-lab/`.

## Editing

- **Small text changes:** edit the page's `index.html` directly (on GitHub: open the file → pencil icon).
- **Add a member / news item:** copy an existing `<section class="block">…</section>` in
  `current-members/index.html` or `news-and-updates/index.html`, change the text, put the photo in
  `assets/img/` and update the `src`.
- **Menu changes:** the menu is repeated in every page. Either edit all pages, or change `NAV`/`PAGES`
  in `tools/build_site.py` and run `python tools/build_site.py` (Python 3.8+, no extra packages;
  it regenerates every page from `tools/content.json` and reuses the images in `assets/img/`).
  Note: regenerating overwrites manual edits to the HTML pages.

Links all use relative paths, so the site works both under `/<repo-name>/` and on a custom domain.
