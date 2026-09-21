# Agerbo Vingaard – website

Static one-page site built from the Claude Design mockups in `design/`, deployed to **Azure Static Web Apps** by GitHub Actions on every push to `main`.

- Wider than 820 px: desktop layout. 820 px or narrower: mobile layout with a bottom tab bar.
- Plain HTML/CSS, no framework and no build step. Fonts are self-hosted, and nothing loads from third parties.

```
site/                      ← what gets deployed
  index.html               desktop + mobile markup
  styles.css               design tokens + layout
  site.js                  contact form (mailto) + active tab highlighting
  staticwebapp.config.json Azure routing, 404, caching, headers
  images/                  put hero.jpg, bier.jpg, besog.jpg here (see README inside)
  fonts/                   Caprasimo + Figtree (woff2)
design/                    original Claude Design exports (reference)
tools/build.py             regenerates site/ from design/ (keeps site/images)
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

- **Photos:** add `hero.jpg`, `bier.jpg` and `besog.jpg` to `site/images/`, then commit and push. Until you do, placeholders show in their place.
- **Text:** edit `site/index.html`. Each section appears twice, once inside `.v-desktop` and once inside `.v-mobile`, so change both.
- **New design export:** replace the files in `design/`, run `python tools/build.py`, then check the result and commit.

## Contact form

A static site has no server, so **Send besked** opens the visitor's mail app with a message to info@agerbogaard.dk already filled in. If you'd rather have messages arrive without the visitor's mail app, connect the form to a service such as Formspree, or to an Azure Function (`api/` folder).
