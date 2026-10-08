# Dr. Anusuya Pal — GitHub Pages Research Website

A static research portfolio for Dr. Anusuya Pal with an automatic ORCID publication synchronization layer.

## Files

- `index.html` — main website
- `styles.css` — visual system and responsive layout
- `script.js` — navigation, animation and publication rendering
- `data/publications.json` — generated ORCID publication feed
- `update_orcid.py` — retrieves public ORCID works
- `.github/workflows/update-orcid.yml` — scheduled GitHub Action

## GitHub Pages setup

1. Create a GitHub repository, e.g. `anusuyapal.github.io`.
2. Upload all files while preserving the directory structure.
3. Open **Settings → Pages**.
4. Under **Build and deployment**, select **Deploy from a branch**.
5. Select `main` and `/ (root)`.
6. Save.
7. If a custom domain is desired later, configure it under **Settings → Pages → Custom domain**.

## ORCID synchronization

The workflow runs once per day and can also be triggered manually:

**GitHub → Actions → Sync ORCID Publications → Run workflow**

It reads public works from:

`https://orcid.org/0000-0002-8573-7938`

and writes them to:

`data/publications.json`

No ORCID password or private token is stored in this repository.

## Important

The site deliberately keeps biography, research themes, funding descriptions and contact details human-curated. ORCID is used as the source of truth for the publication feed.

If the ORCID record changes, the next workflow run updates `publications.json`; GitHub Pages then publishes the changed site automatically.

## Optional next step

For a custom domain, add a `CNAME` file containing the domain name and configure the DNS records at the domain registrar.
