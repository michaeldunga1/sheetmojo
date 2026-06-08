# SheetMojo Deployment Guide

This guide covers deploying SheetMojo to a Hostinger VPS running Ubuntu 24.04 LTS.

---

## Prerequisites

- **Local machine:** Git, SSH client, rsync
- **Hostinger VPS:** Ubuntu 24.04 LTS provisioned, IP address noted
- **Domain name:** Pointing to your VPS IP (or ready to configure DNS)

---

## Quick Start (Automated)

Use the included `deploy.sh` script:

```bash
chmod +x deploy.sh
./deploy.sh 192.168.1.100 deploy yourdomain.com
```

The script will:
1. Copy your app to the server
2. Install dependencies
3. Prompt you to choose PM2 or systemd
4. Configure Nginx
5. Set up HTTPS with Certbot

**Note:** You'll be prompted for an email during Certbot setup.

---

## Manual Deployment (Step-by-Step)

### 1. Provision the VPS

1. Log into **hPanel** → **VPS**
2. Create a new server with **Ubuntu 24.04 LTS**
3. Note the IP address and root password

### 2. Connect and Create a Deployment User

```bash
ssh root@YOUR_SERVER_IP
```

Create a non-root user for better security:

```bash
adduser deploy
usermod -aG sudo deploy
```

Exit and reconnect:

```bash
ssh deploy@YOUR_SERVER_IP
```

### 3. Install System Dependencies

Puppeteer needs several libraries for PDF generation:

```bash
sudo apt update
sudo apt install -y \
  ca-certificates \
  fonts-liberation \
  libatk-bridge2.0-0 \
  libgtk-3-0 \
  libx11-xcb1 \
  libxcomposite1 \
  libxdamage1 \
  libxrandr2 \
  libgbm1 \
  libpango-1.0-0 \
  libcairo2 \
  libxrender1 \
  libxext6 \
  libnss3 \
  libxss1 \
  libasound2 \
  curl \
  git \
  nginx \
  certbot \
  python3-certbot-nginx
```

### 4. Install Node.js via nvm

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install --lts
node --version
npm --version
```

### 5. Clone and Set Up the App

```bash
git clone https://github.com/yourname/sheetmojo.git
cd sheetmojo
npm install --production
```

Create your `.env` file:

```bash
nano .env
```

Example `.env`:

```
HOST=0.0.0.0
PORT=3000
NODE_ENV=production
```

### 6. Choose a Process Manager

#### Option A: PM2 (Recommended)

```bash
npm install -g pm2
pm2 start server.js --name "sheetmojo"
pm2 startup systemd -u deploy --hp /home/deploy
pm2 save
```

Check status:

```bash
pm2 status
pm2 logs sheetmojo
```

#### Option B: systemd (Lightweight)

Copy the service file:

```bash
sudo cp sheetmojo.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sheetmojo
sudo systemctl start sheetmojo
```

Check status:

```bash
sudo systemctl status sheetmojo
sudo journalctl -u sheetmojo -f
```

### 7. Configure Nginx

```bash
sudo cp nginx.conf.example /etc/nginx/sites-available/sheetmojo
sudo nano /etc/nginx/sites-available/sheetmojo
```

Replace `yourdomain.com` with your actual domain. Then:

```bash
sudo ln -s /etc/nginx/sites-available/sheetmojo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. Set Up HTTPS with Certbot

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Certbot will automatically:
- Validate your domain
- Install an SSL certificate
- Update your Nginx config
- Set up auto-renewal

### 9. Open the Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 10. Point Your Domain

In your domain registrar (or Hostinger DNS), create an **A record**:

- **Name:** `@` (for root) and `www`
- **Type:** A
- **Value:** Your VPS IP address

Wait a few minutes for DNS propagation, then visit `https://yourdomain.com`.

---

## Useful Commands

### PM2

```bash
pm2 list                    # List all processes
pm2 status                  # Show process status
pm2 logs sheetmojo          # View logs
pm2 restart sheetmojo       # Restart the app
pm2 stop sheetmojo          # Stop the app
pm2 delete sheetmojo        # Remove from PM2
```

### systemd

```bash
sudo systemctl status sheetmojo             # Check status
sudo systemctl restart sheetmojo            # Restart
sudo systemctl stop sheetmojo               # Stop
sudo journalctl -u sheetmojo -f             # View logs (follow mode)
sudo journalctl -u sheetmojo --lines 50     # Last 50 log lines
```

### Nginx

```bash
sudo nginx -t                      # Test config
sudo systemctl reload nginx        # Reload (zero downtime)
sudo systemctl restart nginx       # Full restart
sudo systemctl status nginx        # Check status
```

### Certbot

```bash
sudo certbot renew --dry-run       # Test renewal
sudo certbot certificates          # List certificates
sudo certbot delete                # Remove a certificate
```

---

## Troubleshooting

### App won't start

1. Check logs:
   ```bash
   pm2 logs sheetmojo          # if using PM2
   sudo journalctl -u sheetmojo -f  # if using systemd
   ```

2. Verify `.env` file exists and is readable:
   ```bash
   cat /home/deploy/sheetmojo/.env
   ```

3. Verify Node.js is installed:
   ```bash
   node --version
   ```

### Nginx error "connection refused"

1. Verify the app is running on port 3000:
   ```bash
   netstat -tuln | grep 3000
   ```

2. Check Nginx config:
   ```bash
   sudo nginx -t
   ```

3. Reload Nginx:
   ```bash
   sudo systemctl reload nginx
   ```

### SSL certificate issues

1. Check certificate expiry:
   ```bash
   sudo certbot certificates
   ```

2. Test renewal:
   ```bash
   sudo certbot renew --dry-run
   ```

3. Force renewal:
   ```bash
   sudo certbot renew --force-renewal
   ```

---

## Security Best Practices

1. **SSH hardening:** Disable root login and password auth (use key-based auth only)
2. **Firewall:** Use `ufw` to restrict access
3. **Node.js security:** Set `NODE_ENV=production` in `.env`
4. **HTTPS only:** Use Nginx to redirect HTTP → HTTPS
5. **Rate limiting:** Consider adding rate limits in Nginx for API endpoints
6. **Monitoring:** Set up uptime monitoring (e.g., UptimeRobot)
7. **Backups:** Regularly back up your VPS

---

## Monitoring & Logs

### Check app health

```bash
curl https://yourdomain.com/healthz
# Should return: ok
```

### Monitor system resources

```bash
top
free -h
df -h
```

### Check process manager

```bash
pm2 monit              # Real-time monitoring (PM2)
ps aux | grep node     # List Node processes
```

---

## Updates & Maintenance

### Update dependencies

```bash
cd /home/deploy/sheetmojo
npm update
pm2 restart sheetmojo
```

### Update Node.js

```bash
nvm install --lts
nvm alias default lts/*
pm2 restart sheetmojo
```

### Restart the app without downtime

```bash
pm2 reload sheetmojo   # Graceful reload (if using PM2)
```

---

## Support

For issues, check:
- `/home/deploy/sheetmojo/.env` — Environment config
- `pm2 logs sheetmojo` — App logs
- `sudo systemctl status nginx` — Nginx status
- Nginx error logs: `/var/log/nginx/error.log`

---

Happy deploying! 🚀
