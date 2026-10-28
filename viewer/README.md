# Open Business Sale Classification explorer

Browse the published [catalogue explorer](https://subtledifference.github.io/open-business-sale-classification/). This guide covers local previews and maintenance of the static, read-only interface. The root homepage loads the canonical `taxonomy/categories.json`; category records, aliases, counts and version metadata are not copied into the viewer.

The three frontend files are root `index.html`, `viewer/styles.css` and `viewer/app.js`. There are no frontend packages, build tools, remote fonts, analytics, backend or stored selections. Browsing and the example builder run in the browser. Only loading the static files and JSON makes requests; selections are not transmitted. Copying JSON uses the browser clipboard, with a manual-copy fallback.

## Run locally

From the repository root in PowerShell:

```powershell
python -m http.server 8765 --bind 127.0.0.1
```

Open **http://127.0.0.1:8765/**. Stop the server with **Ctrl+C**. Use another free port if necessary. Opening `index.html` directly with `file://` does not support the required JSON fetch.

This is Python's standard-library static file server, not an application backend. It is bound to the local computer only.

## Static hosting and GitHub Pages

The explorer's HTML entry point is at the repository root; `viewer/` contains the CSS, JavaScript and this guide.

```text
index.html
.nojekyll
viewer/
  styles.css
  app.js
taxonomy/
  categories.json
```

Serve the repository root with both folders intact. The page references `./viewer/styles.css` and `./viewer/app.js`; its data request is `./taxonomy/categories.json`. These relative paths preserve a project prefix such as `/open-business-sale-classification/`.

For GitHub Pages, use **Deploy from a branch → main → /(root)**. The empty `.nojekyll` skips Jekyll processing; no custom workflow or build framework is required. See the [hosting configuration and deployment checks](../docs/github-pages.md). The published explorer uses the project root URL linked above.

## Behaviour

- Activities are filtered by the 19 industry groups and paginated in sets of 12. The remaining group contains the nine separate Business Characteristics.
- Search uses names, IDs and the supplied aliases. It normalises case, Unicode accents/width, punctuation and common HTML entities. Existing aliases supply spelling variations; there is no fuzzy recommendation engine. Exact matches take priority while legitimate ambiguous matches remain candidates.
- Activity names open a keyboard-accessible dialog with the full description and alias notes. Characteristics show their full descriptions directly.
- The demonstration allows 1–3 activities and independently 0–3 characteristics. Attempts to add a fourth of either kind are rejected with feedback. Characteristics alone remain an incomplete example, and JSON copying stays disabled.
- Generated selection JSON contains the catalogue identity/version and separate `activities` and `characteristics` ID arrays, matching the documented classification model. It establishes neither receiver acceptance nor a feed protocol.
- Reloading clears the example. No cookies or browser storage are used.

## Checks

Run the existing repository checks from its root:

```text
python tools/catalogue.py --check
python -m unittest discover -s tests
```

For browser acceptance, check all groups and pages, aliases and empty results, full detail dialogs, independent selection limits, incomplete examples, clipboard/manual copy, keyboard focus, and narrow/wide layouts. Check loading, missing/malformed JSON and retry behaviour. Modern JavaScript, CSS and native HTML dialog support are required.
