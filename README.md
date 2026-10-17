# Wrocław Tabliczka

Static GitHub Pages app for generating a stop-specific timetable for Wrocław bus and tram lines. The browser does not require the user to upload a GTFS ZIP. A scheduled GitHub Actions workflow downloads the official open-data GTFS feed and rebuilds `data.json` daily.

## Publish
1. Upload all files and the `.github/workflows/update-data.yml` workflow to a GitHub repository (root folder).
2. In **Settings → Actions → General**, ensure workflows can write repository contents if your repository settings require it.
3. Open **Actions → Update official Wroclaw GTFS data → Run workflow** once. This creates `data.json` from the official GTFS feed.
4. In **Settings → Pages**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`.
5. Wait for the Pages deployment and open the published URL.

The workflow runs daily. It uses the public dataset on [OpenData Wrocław](https://open-data.cui.wroclaw.pl/hdb/ft/6/). The generated database includes routes, stops, trip times, service calendars and date exceptions. This is a community tool, not an official MPK product.
