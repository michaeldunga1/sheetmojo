#!/bin/bash

# Deployment script for Swiftener
# Usage: ./deploy.sh <server_ip> <username> <domain>
# Example: ./deploy.sh 192.168.1.100 deploy yourdomain.com

set -e

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <server_ip> <username> <domain>"
  echo "Example: $0 192.168.1.100 deploy yourdomain.com"
  exit 1
fi

SERVER_IP=$1
USERNAME=$2
DOMAIN=$3
APP_NAME="swiftener"
REMOTE_PATH="/home/$USERNAME/$APP_NAME"

echo "🚀 Deploying $APP_NAME to $SERVER_IP as $USERNAME"
echo "Domain: $DOMAIN"
echo ""

# Step 1: Copy app files
echo "📦 Copying app files..."
ssh $USERNAME@$SERVER_IP "mkdir -p $REMOTE_PATH"
rsync -avz --exclude=node_modules --exclude=.git --exclude=.env . $USERNAME@$SERVER_IP:$REMOTE_PATH/

# Step 2: Install dependencies
echo "📚 Installing dependencies..."
ssh $USERNAME@$SERVER_IP "cd $REMOTE_PATH && npm install --production"

# Step 3: Create .env file
echo "⚙️  Setting up .env file..."
ssh $USERNAME@$SERVER_IP "
if [ ! -f $REMOTE_PATH/.env ]; then
  cp $REMOTE_PATH/.env.example $REMOTE_PATH/.env
  echo '✓ .env file created. Update it with your production settings.'
else
  echo '✓ .env file already exists.'
fi
"

# Step 4: Option to set up PM2 or systemd
echo ""
echo "Choose deployment method:"
echo "1) PM2 (automatic restarts, monitoring)"
echo "2) systemd (lightweight, system integration)"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
  echo "🔄 Setting up PM2..."
  ssh $USERNAME@$SERVER_IP "
    npm install -g pm2
    cd $REMOTE_PATH
    pm2 start server.js --name \"$APP_NAME\"
    pm2 startup systemd -u $USERNAME --hp /home/$USERNAME
    pm2 save
  "
  echo "✓ PM2 configured. App will auto-start on reboot."
elif [ "$choice" = "2" ]; then
  echo "🔧 Setting up systemd..."
  ssh $USERNAME@$SERVER_IP "
    sudo cp $REMOTE_PATH/swiftener.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable $APP_NAME
    sudo systemctl start $APP_NAME
  "
  echo "✓ systemd configured. App will auto-start on reboot."
else
  echo "⚠️  No process manager configured. Set up PM2 or systemd manually."
fi

# Step 5: Configure Nginx
echo ""
read -p "Configure Nginx? (y/n): " nginx_choice
if [ "$nginx_choice" = "y" ]; then
  echo "🌐 Setting up Nginx..."
  ssh $USERNAME@$SERVER_IP "
    sudo cp $REMOTE_PATH/nginx.conf.example /etc/nginx/sites-available/$APP_NAME
    sudo sed -i 's/yourdomain.com/$DOMAIN/g' /etc/nginx/sites-available/$APP_NAME
    sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx
  "
  echo "✓ Nginx configured."
fi

# Step 6: Set up HTTPS
echo ""
read -p "Set up HTTPS with Certbot? (y/n): " https_choice
if [ "$https_choice" = "y" ]; then
  echo "🔒 Installing Certbot and setting up HTTPS..."
  ssh $USERNAME@$SERVER_IP "
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN
  "
  echo "✓ HTTPS configured and auto-renewal enabled."
fi

echo ""
echo "✅ Deployment complete!"
echo "App should be running at https://$DOMAIN"
echo ""
echo "Useful commands:"
echo "  ssh $USERNAME@$SERVER_IP"
echo "  pm2 logs $APP_NAME          (if using PM2)"
echo "  sudo journalctl -u $APP_NAME (if using systemd)"
