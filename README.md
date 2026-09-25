# Agerbo Vingaard – website

Static multi-page site, deployed to **Azure Static Web Apps** by GitHub Actions on every push to `main`.

- One set of HTML for every screen size. Wider than 820 px: desktop layout. 820 px or narrower: mobile layout with the menu as a bottom tab bar.
- Plain HTML/CSS, no framework and no build step. `site/` is the source: edit it directly. Fonts are self-hosted, and nothing loads from third parties.

```
site/                      ← what gets deployed, and what you edit
  index.html               Forside              → /
  vine/index.html          Vores vine           → /vine
  vinsmagning/index.html   Vinsmagning          → /vinsmagning
  bigaarden/index.html     Honning og mjød      → /bigaarden
  historien/index.html     Historien            → /historien
  besog-os/index.html      Åbningstider/kontakt → /besog-os
  404.html                 "Siden findes ikke" (not indexed)
  styles.css               design tokens + layout (desktop and mobile)
  site.js                  contact form (mailto)
  robots.txt, sitemap.xml  for search engines
  staticwebapp.config.json Azure routing: clean URLs, 301s from the old Weebly pages, real 404, caching, headers
  images/                  put hero.jpg, bier.jpg, besog.jpg here (see README inside)
  fonts/                   Caprasimo + Figtree (woff2)
design/                    original Claude Design exports (reference only)
.github/workflows/         Azure Static Web Apps deploy workflow
```

## First-time setup (about 10 minutes)

1. **Create the GitHub repo.** On github.com choose New repository, name it `agerbogaard-web`, and leave it empty (no README or .gitignore). Then run this from this folder:
   ```bash
   git remote add origin https://github.com/RasmusThougaardKristensen/agerbogaard-web.git
   git push -u origin main
   ```
   The first workflow run fails because the token isn't set yet. That's expected.

2. **Create the Static Web App** in the Azure portal: *Create a resource → Static Web App*.
   - Plan: **Free**
   - Region: **West Europe**
   - Deployment details: **Other**. This project already has its own workflow, and choosing Other stops Azure from adding a second one.
   - Click Review + create, then Create.

3. **Copy the deployment token.** Open the new Static Web App and choose **Manage deployment token**, then copy the token.

4. **Add it to GitHub.** In the repo go to *Settings → Secrets and variables → Actions → New repository secret*.
   - Name: `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - Value: the token you copied

5. **Deploy.** In the repo open *Actions → Deploy to Azure Static Web Apps → Run workflow*, or just push a commit. When it turns green, the site is live at the URL shown on the Static Web App's Overview page (`https://<name>.azurestaticapps.net`).

Pull requests get their own preview URL automatically, and the preview is removed when the PR closes.

### Or with the Azure CLI

```bash
az group create -n rg-agerbogaard -l westeurope
az staticwebapp create -n agerbogaard-web -g rg-agerbogaard -l westeurope --sku Free
az staticwebapp secrets list -n agerbogaard-web -g rg-agerbogaard --query properties.apiKey -o tsv
```
Put the printed key in the GitHub secret, as in step 4.

## Custom domain (agerbogaard.dk)

In the Static Web App go to *Custom domains → Add*. For `www.agerbogaard.dk`, add a CNAME record at your DNS host pointing to `<name>.azurestaticapps.net`. For the bare `agerbogaard.dk`, use the TXT validation plus the ALIAS/ANAME record Azure shows you. HTTPS certificates are free and set up automatically.

## Everyday edits

- **Photos:** add `hero.jpg`, `bier.jpg` and `besog.jpg` to `site/images/`, then commit and push. Until you do, placeholders show in their place. If a photo shows something other than what its `alt` text says, update the `alt` text in the HTML.
- **Text:** edit the page's `index.html` in `site/`. Each text now exists only once, and it's used on both desktop and mobile.
- **Header, menu and footer** are repeated in each of the 6 pages and in `404.html`. If you change them, change all 7 files (search and replace).
- **News ("Nyt fra gården")** sits in the pink card on the front page and on `/besog-os`. Update or remove it when it's out of date, for example "September 2026".
- **Opening hours** also appear in the structured data (`<script type="application/ld+json">` in `index.html` and `besog-os/index.html`). The seasonal hours are dated. Add the next season each year so Google shows the right hours.
- **New page:** create `site/<name>/index.html` (copy an existing page), give it its own `<title>`, description, canonical and `<h1>`, add it to the menu in every page, and add the URL to `sitemap.xml`.

## SEO checklist at launch

1. Add both `www.agerbogaard.dk` and `agerbogaard.dk` as custom domains. Canonical tags, the sitemap and structured data all use **https://www.agerbogaard.dk**, so make that one the default and redirect the bare domain to it.
2. The old Weebly URLs (`/vinsmagning.html`, `/kontakt.html` …) are 301-redirected in `staticwebapp.config.json`. Test a few after the domain switch.
3. In Google Search Console: verify the domain, submit `https://www.agerbogaard.dk/sitemap.xml`, and check the *Pages* report over the following weeks.
4. Make sure the Google Business Profile has the same address, phone and opening hours as the site.

## Contact form

A static site has no server, so **Send besked** opens the visitor's mail app with a message to info@agerbogaard.dk already filled in. If you'd rather have messages arrive without the visitor's mail app, connect the form to a service such as Formspree, or to an Azure Function (`api/` folder).
