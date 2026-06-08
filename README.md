# SheetMojo

A lightweight productivity site for VPS deployment. It includes:

- Web page to PDF converter
- YouTube audio/video downloader
- Excel to JSON/CSV converter
- CSV to JSON converter
- CSV/JSON to chart converter
- Character counter
- Word counter

## Deployment

1. Install dependencies:

```bash
npm install
```

2. Start the server:

```bash
npm start
```

> Requires Node.js 22.12 or newer for Puppeteer compatibility.

3. Open the app in your browser at:

```text
http://localhost:3000
```

## VPS deployment on Ubuntu 24.04 LTS

1. Install system packages required by Puppeteer:

```bash
sudo apt update && sudo apt install -y ca-certificates fonts-liberation libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libxrender1 libxext6 libnss3 libxss1 libasound2
```

2. Install Node.js 22 or later and npm, then install dependencies:

```bash
npm install
```

3. Copy environment defaults into `.env`:

```bash
cp .env.example .env
```

4. Start the app on the public interface:

```bash
npm run start:prod
```

4. Recommended production options:

- Use `pm2` or `systemd` to keep the app running after reboot.
- Use the included `ecosystem.config.js` if you deploy with PM2:

```bash
pm install -g pm2
pm start
# or
pm run start:prod
pm2 start ecosystem.config.js
```
- Set `NODE_ENV=production` for optimized middleware behavior.
- Use `PORT` and `HOST` environment variables to control binding.
- Keep the app behind a firewall or reverse proxy if exposing it to the public internet.

## VPS recommendations

- Use `pm2`, `systemd`, or a process manager to keep the app running.
- Bind the app to `0.0.0.0` for external access.
- Set `PORT` in the environment if needed.
- Ensure the server has the dependencies needed for Puppeteer and headless Chrome.
- `GET /robots.txt` and `GET /sitemap.xml` are available for search engine indexing.

## Health check

- `GET /healthz` returns `ok`

## Notes

- Static assets are served with caching enabled.
- `helmet` and `compression` are used for security and performance.
