const express = require('express');
const path = require('path');
const compression = require('compression');
const helmet = require('helmet');
const ytdl = require('ytdl-core');
const puppeteer = require('puppeteer');
const app = express();
const isProduction = process.env.NODE_ENV === 'production';
let browser;

app.disable('x-powered-by');
app.set('trust proxy', 1);
app.use(compression());
app.use(helmet({ contentSecurityPolicy: false }));
app.use(express.json());

const prettyRedirects = {
  '/index.html': '/',
  '/pdf.html': '/pdf',
  '/youtube.html': '/youtube',
  '/csv-json.html': '/csv-json',
  '/excel.html': '/excel',
  '/chart.html': '/chart',
  '/char-counter.html': '/char-counter',
  '/word-counter.html': '/word-counter'
};

app.get(Object.keys(prettyRedirects), (req, res) => {
  res.redirect(301, prettyRedirects[req.path]);
});

app.get('/robots.txt', (req, res) => {
  res.type('text/plain');
  res.send(`User-agent: *\nAllow: /\nSitemap: ${req.protocol}://${req.get('host')}/sitemap.xml\n`);
});

app.get('/sitemap.xml', (req, res) => {
  const baseUrl = `${req.protocol}://${req.get('host')}`;
  const routes = ['/', '/pdf', '/youtube', '/csv-json', '/excel', '/chart', '/char-counter', '/word-counter'];
  const urls = routes.map(path => `  <url>\n    <loc>${baseUrl}${path}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>${path === '/' ? '1.0' : '0.8'}</priority>\n  </url>`).join('\n');

  res.type('application/xml');
  res.send(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>`);
});

app.use(express.static(path.join(__dirname, 'public'), {
  maxAge: '7d',
  immutable: true,
  setHeaders(res, filePath) {
    if (filePath.endsWith('.html')) {
      res.setHeader('Cache-Control', 'public, max-age=0, must-revalidate');
    }
  }
}));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/pdf', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'pdf.html'));
});

app.get('/youtube', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'youtube.html'));
});

app.get('/csv-json', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'csv-json.html'));
});

app.get('/excel', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'excel.html'));
});

app.get('/chart', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'chart.html'));
});

app.get('/char-counter', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'char-counter.html'));
});

app.get('/word-counter', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'word-counter.html'));
});

function parseCsv(csvText) {
  const rows = [];
  let row = [];
  let cell = '';
  let inQuotes = false;

  for (let i = 0; i < csvText.length; i++) {
    const char = csvText[i];
    const next = csvText[i + 1];

    if (inQuotes) {
      if (char === '"') {
        if (next === '"') {
          cell += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        cell += char;
      }
      continue;
    }

    if (char === '"') {
      inQuotes = true;
      continue;
    }

    if (char === ',') {
      row.push(cell);
      cell = '';
      continue;
    }

    if (char === '\n' || char === '\r') {
      if (char === '\r' && next === '\n') {
        i++;
      }
      row.push(cell);
      rows.push(row);
      row = [];
      cell = '';
      continue;
    }

    cell += char;
  }

  if (cell.length > 0 || row.length > 0) {
    row.push(cell);
    rows.push(row);
  }

  return rows;
}

async function getBrowser() {
  if (browser && browser.isConnected()) {
    return browser;
  }

  browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    headless: 'new'
  });

  return browser;
}

async function closeBrowser() {
  if (browser && browser.isConnected()) {
    await browser.close();
  }
  browser = null;
}

function shutdown(code) {
  console.log(`Shutting down (${code})`);
  closeBrowser().finally(() => process.exit(0));
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('uncaughtException', async err => {
  console.error('Uncaught exception', err);
  await closeBrowser();
  process.exit(1);
});
process.on('unhandledRejection', async reason => {
  console.error('Unhandled rejection', reason);
  await closeBrowser();
  process.exit(1);
});

app.get('/api/page-to-pdf', async (req, res) => {
  const rawUrl = String(req.query.url || '').trim();
  if (!rawUrl) {
    return res.status(400).json({ error: 'A URL is required.' });
  }
  const url = rawUrl.match(/^https?:\/\//i) ? rawUrl : `http://${rawUrl}`;

  try {
    const browserInstance = await getBrowser();
    const page = await browserInstance.newPage();
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
    const pdfBuffer = await page.pdf({ format: 'A4', printBackground: true, margin: { top: '12mm', right: '12mm', bottom: '12mm', left: '12mm' } });
    await page.close();

    res.set({
      'Content-Type': 'application/pdf',
      'Content-Disposition': 'attachment; filename="page.pdf"'
    });
    res.send(pdfBuffer);
  } catch (error) {
    res.status(500).json({ error: 'Unable to convert the page to PDF.', details: error.message });
  }
});

app.get('/api/youtube', async (req, res) => {
  const url = String(req.query.url || '').trim();
  const type = String(req.query.type || 'audio').toLowerCase();

  if (!ytdl.validateURL(url)) {
    return res.status(400).json({ error: 'A valid YouTube URL is required.' });
  }

  try {
    if (type === 'video') {
      const info = await ytdl.getInfo(url);
      const format = ytdl.chooseFormat(info.formats, {
        quality: 'highest',
        filter: format => format.hasVideo && format.hasAudio && format.container === 'mp4'
      }) || ytdl.chooseFormat(info.formats, { quality: 'highest', filter: 'audioandvideo' });

      if (!format) {
        return res.status(500).json({ error: 'Unable to locate a downloadable video format.' });
      }

      const contentType = format.mimeType ? format.mimeType.split(';')[0] : 'video/mp4';
      res.set({
        'Content-Type': contentType,
        'Content-Disposition': 'attachment; filename="youtube-video.mp4"'
      });

      const stream = ytdl(url, { format });
      stream.on('error', errorHandler);
      res.on('close', () => stream.destroy());
      return stream.pipe(res);
    }

    res.set({
      'Content-Type': 'audio/mp4',
      'Content-Disposition': 'attachment; filename="youtube-audio.m4a"'
    });

    const stream = ytdl(url, { filter: 'audioonly', quality: 'highestaudio' });
    stream.on('error', errorHandler);
    res.on('close', () => stream.destroy());
    return stream.pipe(res);
  } catch (error) {
    return sendYoutubeError(error);
  }

  function errorHandler(error) {
    sendYoutubeError(error);
  }

  function sendYoutubeError(error) {
    if (res.headersSent) {
      res.end();
      return;
    }
    res.status(500).json({ error: 'Unable to process the YouTube request.', details: error.message });
  }
});

app.get('/api/csv2json', (req, res) => {
  const csv = String(req.query.csv || '').trim();
  if (!csv) {
    return res.status(400).json({ error: 'CSV input is required.' });
  }

  try {
    const rows = parseCsv(csv);
    if (!rows.length) {
      return res.json({ data: [] });
    }

    const headers = rows[0].map(header => String(header || '').trim());
    const data = rows.slice(1).map(row => {
      const object = {};
      headers.forEach((header, index) => {
        object[header || `column_${index + 1}`] = row[index] ?? '';
      });
      return object;
    });

    res.json({ data });
  } catch (error) {
    res.status(400).json({ error: 'Invalid CSV input.' });
  }
});

app.get('/healthz', (req, res) => {
  res.status(200).send('ok');
});

app.use((req, res) => {
  res.status(404).send('Not found');
});

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

module.exports = app;