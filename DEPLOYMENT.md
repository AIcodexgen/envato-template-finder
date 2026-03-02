# 🚀 Deployment Guide

## Deploy to Render (Recommended - Free Tier)

1. **Push to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/envato-template-finder.git
git push -u origin main
```

2. **Create New Web Service on Render:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

3. **Configure Service:**
   - **Name:** envato-template-finder
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt && playwright install chromium`
   - **Start Command:** `python main.py`
   - **Plan:** Free

4. **Add Environment Variables:**
   - Click "Advanced" → "Add Environment Variable"
   - Key: `GOOGLE_API_KEY`
   - Value: Your Google API key

5. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Your app will be live at `https://envato-template-finder.onrender.com`

## Deploy to Railway

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Login and Initialize:**
```bash
railway login
railway init
```

3. **Add Environment Variables:**
```bash
railway variables set GOOGLE_API_KEY=your_key_here
```

4. **Deploy:**
```bash
railway up
```

## Deploy to Heroku

1. **Create Heroku App:**
```bash
heroku create envato-template-finder
```

2. **Set Buildpacks:**
```bash
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/mxschmitt/heroku-playwright-buildpack.git
```

3. **Configure Environment:**
```bash
heroku config:set GOOGLE_API_KEY=your_key_here
heroku config:set PLAYWRIGHT_BROWSERS_PATH=0
```

4. **Create Procfile:**
```
web: python main.py
```

5. **Deploy:**
```bash
git push heroku main
```

## Deploy with Docker

### Local Docker
```bash
# Build image
docker build -t envato-finder .

# Run container
docker run -p 8000:8000 -e GOOGLE_API_KEY=your_key envato-finder
```

### Docker Compose
```bash
# Create .env file first
echo "GOOGLE_API_KEY=your_key" > .env

# Run
docker-compose up -d
```

## Deploy to AWS (EC2)

1. **Launch EC2 Instance:**
   - AMI: Ubuntu Server 22.04 LTS
   - Instance Type: t3.medium (minimum for Playwright)
   - Security Group: Allow port 8000

2. **SSH and Setup:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update and install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv

# Clone repository
git clone https://github.com/YOUR_USERNAME/envato-template-finder.git
cd envato-template-finder

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Create .env file
echo "GOOGLE_API_KEY=your_key" > .env

# Run with nohup
nohup python main.py > app.log 2>&1 &
```

3. **Setup Nginx (Optional):**
```bash
sudo apt install nginx

# Create config
sudo tee /etc/nginx/sites-available/envato-finder << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/envato-finder /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Deploy to DigitalOcean App Platform

1. **Create App:**
   - Go to [cloud.digitalocean.com](https://cloud.digitalocean.com)
   - Click "Create" → "Apps"
   - Select GitHub repository

2. **Configure:**
   - **Type:** Web Service
   - **Build Command:** `pip install -r requirements.txt && playwright install chromium`
   - **Run Command:** `python main.py`
   - **Instance Size:** Basic (\$5/month minimum)

3. **Environment Variables:**
   - Add `GOOGLE_API_KEY`

4. **Deploy**

## Environment-Specific Notes

### Render (Free Tier)
- ⚠️ Free tier has 512MB RAM which may be tight for Playwright
- May experience cold starts (15-30 seconds)
- Consider upgrading to Starter tier (\$7/month) for better performance

### Railway
- Good free tier with \$5 credit monthly
- Automatic HTTPS
- Easy environment variable management

### Heroku
- ⚠️ Heroku's ephemeral filesystem means Playwright browsers must be installed on each deploy
- Use the Playwright buildpack (included in instructions)
- May need to configure swap space for browser operations

### AWS/GCP/Azure
- Recommended instance: 2GB RAM minimum
- Install Playwright dependencies:
```bash
sudo apt-get install -y libgbm1 libasound2 libxss1 libnss3
```

## Post-Deployment Checklist

- [ ] App loads without errors
- [ ] Can analyze reference websites
- [ ] Can search and return templates
- [ ] AI matching works (if API key configured)
- [ ] Error handling works (try invalid URL)
- [ ] Responsive design works on mobile
- [ ] Loading states display correctly

## Troubleshooting Deployment

### "Browser not found" Error
```bash
# Reinstall Playwright browsers
playwright install chromium --with-deps
```

### Memory Issues
- Increase RAM to 2GB minimum
- Or disable AI matching (remove GOOGLE_API_KEY)

### Timeout Errors
- Increase timeout values in scraper.py
- Check if target site blocks your IP

### CORS Errors
- FastAPI handles CORS automatically
- If using reverse proxy, ensure headers are forwarded
