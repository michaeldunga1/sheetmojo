# Swiftener

A lightweight productivity site deployed at [swiftener.com](https://swiftener.com). It includes:

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

## SSH Setup

### How to Create SSH Keys

SSH keys provide secure, password-free authentication to your VPS. Generate a key pair on your local machine:

```bash
ssh-keygen -t ed25519 -C "michaeldunga1@gmail.com"
```

When prompted:
- **File location:** Press Enter to use the default (`~/.ssh/id_ed25519`)
- **Passphrase:** Leave blank (or set one for extra security)

This creates:
- `~/.ssh/id_ed25519` (private key — keep this safe!)
- `~/.ssh/id_ed25519.pub` (public key — share this)

View your public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

### How to Connect to the VPS

#### Option 1: Using Password (Initial Setup)

```bash
ssh root@187.124.118.77
```

Hostinger provides the root password in hPanel. After logging in:

1. Create a non-root user for security:

```bash
adduser dunga
usermod -aG sudo dunga
exit
```

2. Reconnect as the new user:

```bash
ssh dunga@187.124.118.77
```

#### Option 2: Using SSH Keys (Recommended for Automation)

1. **Add your public key to the server:**

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub dunga@187.124.118.77
```

2. **Connect without a password:**

```bash
ssh dunga@187.124.118.77
```

#### Option 3: Manual SSH Key Setup

If `ssh-copy-id` doesn't work:

```bash
ssh dunga@187.124.118.77 "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
cat ~/.ssh/id_ed25519.pub | ssh dunga@187.124.118.77 "cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
ssh dunga@187.124.118.77
```

#### SSH Config (Recommended)

Create a shortcut by editing `~/.ssh/config` on your local machine:

```
Host swiftener
    HostName 187.124.118.77
    User dunga
    IdentityFile ~/.ssh/id_ed25519
```

Then simply use:

```bash
ssh swiftener
```

#### Useful SSH Commands

```bash
ssh swiftener                          # Connect to the server
ssh swiftener "command"                # Run a remote command
scp file.txt swiftener:~               # Copy a file to the server
scp -r folder swiftener:~             # Copy a folder recursively
```

## GitHub-based Deployment Routine

Use GitHub as the source of truth and deploy from the VPS with a simple clone or pull.

### Clone the repo on the VPS

```bash
cd ~
git clone git@github.com:michaeldunga1/swiftener.git
cd swiftener
```

### Update an existing deployment

```bash
cd ~/swiftener
git pull origin main
```

### Install dependencies and configure environment

```bash
PUPPETEER_SKIP_DOWNLOAD=true npm install --omit=dev
cp .env.example .env
nano .env
```

### Start or restart the app

```bash
npm install -g pm2
pm2 start server.js --name swiftener
pm2 save
```

### Deploy workflow

1. Make changes locally.
2. Commit and push to GitHub:

```bash
git add -A
git commit -m "Your message"
git push origin main
```

3. Pull the update on the VPS:

```bash
cd ~/swiftener
git pull origin main
PUPPETEER_SKIP_DOWNLOAD=true npm install --omit=dev
pm2 restart swiftener
```

## VPS Deployment on Ubuntu 24.04 LTS (Hostinger)

**Server IP:** `187.124.118.77`  
**User:** `dunga`  
**App directory:** `~/swiftener`  
**Domain:** [swiftener.com](https://swiftener.com)  
**Process manager:** PM2  
**Reverse proxy:** nginx  
**SSL:** Let's Encrypt via Certbot  

1. Install system packages required by Puppeteer:

```bash
sudo apt update && sudo apt install -y ca-certificates fonts-liberation libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libxrender1 libxext6 libnss3 libxss1 libasound2 chromium-browser
```

2. Install Node.js 22 or later, then install dependencies (skipping Puppeteer's Chrome download since system Chromium is used):

```bash
PUPPETEER_SKIP_DOWNLOAD=true npm install --omit=dev
```

3. Copy environment defaults into `.env`:

```bash
cp .env.example .env
nano .env
```

4. Start the app with PM2:

```bash
npm install -g pm2
pm2 start server.js --name swiftener
pm2 save
pm2 startup
```

5. Configure nginx reverse proxy at `/etc/nginx/sites-available/swiftener`:

```nginx
server {
    server_name swiftener.com www.swiftener.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/swiftener.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/swiftener.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if ($host = www.swiftener.com) { return 301 https://$host$request_uri; }
    if ($host = swiftener.com) { return 301 https://$host$request_uri; }
    listen 80;
    server_name swiftener.com www.swiftener.com;
    return 404;
}
```

6. Enable the site and get SSL certificate:

```bash
sudo ln -s /etc/nginx/sites-available/swiftener /etc/nginx/sites-enabled/
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d swiftener.com -d www.swiftener.com
sudo nginx -t && sudo systemctl reload nginx
```

## Puppeteer Notes

Puppeteer is configured to use the system-installed Chromium instead of downloading its own:

```js
const browser = await puppeteer.launch({
    executablePath: '/usr/bin/chromium-browser',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
});
```

The `.npmrc` file in the project root sets `PUPPETEER_SKIP_DOWNLOAD=true` to prevent Chrome downloads during `npm install`.

## VPS Recommendations

- Use PM2 to keep the app running after reboot (`pm2 startup && pm2 save`).
- App binds to `0.0.0.0:3000` and is proxied through nginx on ports 80/443.
- Set `NODE_ENV=production` for optimized middleware behavior.
- Use `PORT` and `HOST` environment variables to control binding.

## Health Check

```bash
curl https://swiftener.com/healthz
# returns: ok
```

## Notes

- Static assets are served with caching enabled.
- `helmet` and `compression` are used for security and performance.
- `GET /robots.txt` and `GET /sitemap.xml` are available for search engine indexing.