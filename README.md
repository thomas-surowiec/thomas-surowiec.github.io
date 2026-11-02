# thomas-surowiec.github.io

Personal academic website, served by GitHub Pages from this repository.

## How it works

The pages are plain HTML, built by a short Python script from data files and templates:

```
_data/site.yaml           name, e-mail, profile links, menu, research-theme texts
_data/publications.yaml   all papers and preprints
_data/seminar.yaml        OiO seminar talks
_templates/*.html         page layouts (rarely need changing)
assets/                   CSS, fonts, images, JavaScript
adverts/, research/       PDFs (seminar abstracts, CV, accepted manuscripts)
tools/build.py            the build script
```

The build writes `index.html`, `research.html`, `publications.html`, `seminar.html` and
`404.html` into the repository root. **Commit those generated files too**: GitHub Pages
serves them as they are (the empty `.nojekyll` file tells GitHub not to post-process anything).

## Everyday tasks

One-time setup (any Python 3.8+):

```bash
pip install jinja2 pyyaml
```

**Add a paper.** Open `_data/publications.yaml`, copy an existing entry, edit it, then:

```bash
python3 tools/build.py
```

Order in the file does not matter; the script sorts by year with preprints on top. When a
preprint is published, change `kind: preprint` to `kind: journal`, set the `year`, and add
`venue`, `details` and the `doi`.

**Update the CV.** Put the new PDF in `research/` and change `cv:` and the CV entry in `nav:`
in `_data/site.yaml`, then rebuild.

**Change the e-mail.** Edit `email_user` / `email_domain` in `_data/site.yaml`. Delete both lines to
remove the address from the site. The address is assembled by JavaScript in the browser, so it
never appears as plain text in the HTML that spam harvesters scan.

**Edit research texts.** They live under `themes:` in `_data/site.yaml`. The `papers:` list
of each theme refers to entries in `publications.yaml` by DOI or arXiv ID.

## Preview locally

```bash
python3 tools/build.py
python3 -m http.server 8000
# then open http://localhost:8000
```

(Opening the files directly with a double-click also works, but browsers block the subtle
contour graphic in the header for `file://` pages.)

## Publish

```bash
git add -A
git commit -m "Update website"
git push
```

GitHub Pages updates within a minute or two.

## Design notes

- Typefaces: STIX Two Text (text) and Source Sans 3 (interface), both SIL Open Font License,
  self-hosted in `assets/fonts/` so no requests go to Google.
- Colours are defined once as variables at the top of `assets/css/style.css`; a dark
  palette follows the visitor's system setting.
- The header graphic `assets/img/contours.svg` shows level sets of a smooth random landscape.
