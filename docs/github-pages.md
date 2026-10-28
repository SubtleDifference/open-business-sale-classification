# GitHub Pages for Open Business Sale Classification

The explorer is published at **[Open Business Sale Classification](https://subtledifference.github.io/open-business-sale-classification/)** from the public [repository](https://github.com/SubtleDifference/open-business-sale-classification). This guide covers hosting configuration, local verification and deployment checks for maintainers.

## Publishing source

Use **Deploy from a branch**, **main**, **/(root)**. The root `index.html` is the explorer itself, not a redirect or iframe. The empty root `.nojekyll` disables Jekyll processing. There is no build command, package installation, custom domain or repository-defined Actions workflow.

GitHub still runs its managed Pages deployment workflow for branch publishing; no custom workflow file is needed. This follows GitHub's [publishing-source documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) and [static-site guidance](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).

## Files and paths

Publish the approved repository contents with this layout intact:

```text
index.html
.nojekyll
viewer/
  styles.css
  app.js
taxonomy/
  categories.json
  categories.csv
LICENSE
```

The HTML references `./viewer/styles.css` and `./viewer/app.js`. JavaScript fetches `./taxonomy/categories.json` relative to the document URL. Download links also stay within the project prefix. The JSON remains the only runtime taxonomy source.

For a project at `/open-business-sale-classification/`, the corresponding paths are:

| Resource | URL path |
| --- | --- |
| Explorer | `/open-business-sale-classification/` |
| Styles | `/open-business-sale-classification/viewer/styles.css` |
| JavaScript | `/open-business-sale-classification/viewer/app.js` |
| Catalogue | `/open-business-sale-classification/taxonomy/categories.json` |

Do not select `/docs` or publish only `viewer/`: the entry point and required data are in the repository root layout. No domain, repository name or absolute site-root path is embedded in the frontend.

## Configuration and deployment checks

The site is already published. To inspect or reproduce its branch-based configuration:

1. Open the repository's **Settings → Pages**.
2. Under **Build and deployment → Source**, use **Deploy from a branch**.
3. Use **main** and **/(root)**. Save only when an authorised configuration change is needed. No custom domain is required.
4. After approved changes are pushed to the publishing source, check the managed **Pages build and deployment** run. If organisation policy blocks deployment, have an authorised owner review it.
5. Use **Visit site** to check the [published explorer](https://subtledifference.github.io/open-business-sale-classification/). Confirm that styles and data load, search works, and a valid example JSON can be copied. Check that the JSON download contains the expected catalogue version.

Changes pushed to the publishing source update the live site. Review the draft scope and [v1.0 roadmap](../ROADMAP.md) as relevant; publication does not imply a stable v1.0 release or industry endorsement.

## Verify locally

From the repository root:

```powershell
python -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/`, then stop with Ctrl+C. For a clone directory named `open-business-sale-classification`, serve its parent directory to verify `http://127.0.0.1:8765/open-business-sale-classification/` with the same project-prefix structure as Pages. A differently named clone uses its own directory name as the prefix.

Run the existing checks before an approved release:

```text
python tools/catalogue.py --check
python -m unittest discover -s tests
```

Local checks verify the root entry point and relative paths under a project prefix. After each deployment, check the published site as well; a successful local preview alone does not establish successful hosted delivery.
