# GitHub Pages for Open Business Sale Classification

The explorer is prepared for the **root URL of a project site** at `https://subtledifference.github.io/open-business-sale-classification/`, using the intended repository `SubtleDifference/open-business-sale-classification`. This guide describes deployment after publication approval; the snapshot itself does not deploy anything.

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

## Activate only after publication approval

1. Review the draft scope and [release checklist](../ROADMAP.md). Obtain explicit approval for repository publication and site deployment.
2. Publish the approved files to `SubtleDifference/open-business-sale-classification` on `main`. Keep the root layout intact.
3. In the publication repository, open **Settings → Pages**.
4. Under **Build and deployment → Source**, choose **Deploy from a branch**.
5. Choose **main** and **/(root)**, then **Save**. Leave the custom-domain field empty.
6. Wait for the managed **Pages build and deployment** run to finish. If it is blocked by organisation policy, have an authorised owner review that policy; do not add a custom workflow as a workaround.
7. Use **Visit site** in Pages settings. The default URL for the intended owner/name is `https://subtledifference.github.io/open-business-sale-classification/`; use the actual site URL displayed by GitHub.
8. Check that the address stays at the project root, styles and data load, search works, and a valid example JSON can be copied. Confirm the JSON download returns the released catalogue version. Subsequent approved pushes to the publishing source update the site.

Enabling Pages is a separate publication action. Use the local preview below while reviewing a draft.

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

Local browser testing verifies the root entry point and relative requests under a project prefix. Actual GitHub-hosted delivery, organisation permissions and deployment completion remain unverified until Pages is explicitly enabled and deployed after approval.
