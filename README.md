# Rates

A home-screen web app showing the 5, 7 and 10-year Treasury par yields and SOFR (plus its 30-day average). It works without the Claude app.

- `index.html`: the app (tiles, Treasury chart with 12M/6M/3M/1W ranges, SOFR chart, daily history)
- `data/rates.json`: the numbers, refreshed by `scripts/update_data.py`
- `.github/workflows/update-data.yml`: runs that script on weekdays at ~9:30am and ~4:45pm ET and commits fresh data
- `manifest.webmanifest`, `sw.js`, `icons/`: home-screen icon, full-screen mode, and offline use (it shows the last data it loaded)

Sources: U.S. Treasury daily par yield curve and the New York Fed's SOFR / SOFR averages, both public with no API key.

## Put it online (one time, free)

1. Create a GitHub account if you don't have one, then a **new public repository** named `tims-yields`.
2. Upload everything in this folder to it, including the hidden `.github` folder. (You can use `git push` or drag and drop on the repo's web page.)
3. In the repo, go to **Settings → Pages**. Under "Build and deployment", pick **Deploy from a branch**, branch `main`, folder `/ (root)`, then Save.
4. Go to **Settings → Actions → General → Workflow permissions** and choose **Read and write permissions**, so the daily job can save new data.
5. Under **Actions → Update rates**, click **Run workflow** once to check it works.

Your app is at https://ratesbytim.com (the old timwcaffrey-web.github.io/tims-yields link redirects there).

## Put it on your iPhone

1. Open that link in **Safari**.
2. Tap **Share → Add to Home Screen → Add**.
3. Delete the old Claude shortcut.

It opens full-screen with your logo. Tap **Refresh** or reopen the app to load the latest numbers.

## Update the data by hand

```bash
python3 scripts/update_data.py
```
