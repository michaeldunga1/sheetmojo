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

## SSH Setup

### How to Create SSH Keys

SSH keys provide secure, password-free authentication to your VPS. Generate a key pair on your local machine:

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
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

### How to Connect to a VPS Server

#### Option 1: Using Password (Initial Setup)

On your local machine, connect via SSH:

```bash
ssh root@YOUR_SERVER_IP
```

Hostinger provides the root password in hPanel. After logging in:

1. Create a non-root user for security:

```bash
adduser deploy
usermod -aG sudo deploy
exit
```

2. Reconnect as the new user:

```bash
ssh deploy@YOUR_SERVER_IP
```

#### Option 2: Using SSH Keys (Recommended for Automation)

1. **Add your public key to the server:**

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub deploy@YOUR_SERVER_IP
```

2. **Connect without a password:**

```bash
ssh deploy@YOUR_SERVER_IP
```

#### Option 3: Manual SSH Key Setup

If `ssh-copy-id` doesn't work:

1. Create the `.ssh` directory on the server:

```bash
ssh deploy@YOUR_SERVER_IP "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
```

2. Copy your public key to the server:

```bash
cat ~/.ssh/id_ed25519.pub | ssh deploy@YOUR_SERVER_IP "cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

3. Test the connection:

```bash
ssh deploy@YOUR_SERVER_IP
```

#### SSH Config (Optional)

Create a shortcut by editing `~/.ssh/config` on your local machine:

```
Host sheetmojo
    HostName YOUR_SERVER_IP
    User deploy
    IdentityFile ~/.ssh/id_ed25519
```

Then simply use:

```bash
ssh sheetmojo
```

#### Useful SSH Commands

```bash
ssh deploy@YOUR_SERVER_IP              # Connect to the server
ssh deploy@YOUR_SERVER_IP "command"    # Run a remote command
scp file.txt deploy@YOUR_SERVER_IP:~   # Copy a file to the server
scp -r folder deploy@YOUR_SERVER_IP:~  # Copy a folder recursively
```

## GitHub-based deployment routine

Use GitHub as the source of truth and deploy from your VPS with a simple clone or pull.

### Clone the repo on the VPS

```bash
cd ~
git clone git@github.com:michaeldunga1/sheetmojo.git
cd sheetmojo
```

If you prefer HTTPS:

```bash
git clone https://github.com/michaeldunga1/sheetmojo.git
cd sheetmojo
```

### Update an existing deployment

```bash
cd ~/sheetmojo
git pull origin main
```

### Install dependencies and configure environment

```bash
npm install --production
cp .env.example .env
nano .env
```

### Start or restart the app

Use PM2:

```bash
npm install -g pm2
pm2 start server.js --name sheetmojo
pm2 save
```

Or use systemd:

```bash
sudo cp sheetmojo.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sheetmojo
sudo systemctl restart sheetmojo
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
cd ~/sheetmojo
git pull origin main
npm install --production
pm2 restart sheetmojo
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
