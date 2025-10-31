# XMRT-DAO-Ecosystem Vercel Deployment Guide

## Overview
This guide explains how to deploy the XMRT-DAO-Ecosystem to Vercel's serverless platform.

## Files Added for Vercel

### 1. `api/index.py`
- Entry point for Vercel's Python runtime
- Imports the Flask app from `app.py`
- Sets environment variables for serverless execution
- Configures simulation mode for MESHNET (hardware not available in serverless)

### 2. `vercel.json`
- Vercel configuration file
- Specifies Python runtime version (3.9)
- Routes all requests to the Flask app
- Sets environment variables for production

### 3. `requirements-vercel.txt` (Optional)
- Optimized dependencies for serverless deployment
- Excludes hardware-dependent packages (Meshtastic, pyserial, ping3)
- If you want to use this, rename it to `requirements.txt` or configure Vercel to use it

### 4. `.vercelignore`
- Excludes unnecessary files from deployment
- Reduces deployment size and time

## Deployment Steps

### Option 1: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd /path/to/XMRT-DAO-Ecosystem
   vercel
   ```

4. **Follow the prompts:**
   - Set up and deploy? **Y**
   - Which scope? **Select your account**
   - Link to existing project? **N** (first time) or **Y** (subsequent)
   - What's your project's name? **xmrt-dao-ecosystem**
   - In which directory is your code located? **./**

5. **Deploy to production**
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository: `DevGruGold/XMRT-DAO-Ecosystem`
4. Vercel will automatically detect the configuration from `vercel.json`
5. Click "Deploy"

### Option 3: Deploy via GitHub Integration (Recommended)

1. Connect your GitHub repository to Vercel
2. Push changes to the main branch
3. Vercel automatically deploys on every push
4. Production URL will be provided

## Environment Variables

### Required (Already set in vercel.json)
- `MESH_PORT=simulate` - Uses simulation mode (no hardware)
- `MESH_UPDATE_INTERVAL=30` - Update interval in seconds
- `FLASK_ENV=production` - Production environment

### Optional (Set in Vercel Dashboard if needed)
- `SECRET_KEY` - Flask secret key (auto-generated if not set)
- `UPSTASH_REDIS_URL` - Redis URL for event bus
- `UPSTASH_REDIS_TOKEN` - Redis token for authentication
- `OPENAI_API_KEY` - OpenAI API key for agent capabilities

To add environment variables:
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add variables for Production, Preview, and Development environments

## Important Notes

### Serverless Limitations
1. **No Hardware Access**: Meshtastic hardware features will run in simulation mode
2. **Cold Starts**: First request may take longer (2-5 seconds)
3. **Execution Time Limit**: Vercel has a 10-second timeout for Hobby plan, 60 seconds for Pro
4. **Memory Limit**: 1024 MB for Hobby plan, 3008 MB for Pro

### Simulation Mode
The app automatically uses simulation mode on Vercel:
- No physical Meshtastic devices required
- Simulated mesh nodes for testing
- All APIs work normally with simulated data

### Background Tasks
Vercel is stateless, so background tasks don't persist between requests. Consider:
- Using Vercel Cron Jobs for scheduled tasks
- External task queue (Upstash, Redis, etc.)
- Webhook-based event triggers

## Testing Your Deployment

After deployment, test these endpoints:

```bash
# Health check
curl https://your-app.vercel.app/health

# API status
curl https://your-app.vercel.app/api/meshnet/status

# Mining stats
curl https://your-app.vercel.app/api/dashboard

# Chatbot UI
open https://your-app.vercel.app/
```

## Troubleshooting

### Build Fails
- Check Python version compatibility (3.9 recommended)
- Verify all imports are available in requirements.txt
- Check build logs in Vercel Dashboard

### Cold Start Timeout
- Optimize imports (lazy loading)
- Reduce dependencies
- Consider upgrading to Vercel Pro

### Module Not Found Errors
- Ensure all dependencies are in requirements.txt
- Check that file paths are correct
- Verify Python path configuration in api/index.py

## Performance Optimization

1. **Lazy Loading**: Import heavy modules only when needed
2. **Caching**: Use Redis (Upstash) for caching
3. **Connection Pooling**: Reuse HTTP connections
4. **Async Operations**: Use async/await for I/O operations

## Monitoring

- **Vercel Analytics**: Built-in analytics in dashboard
- **Logs**: View real-time logs in Vercel Dashboard
- **Health Check**: Monitor `/health` endpoint
- **Uptime Monitoring**: Use external services (UptimeRobot, Pingdom)

## Continuous Deployment

Vercel automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "Update deployment configuration"
git push origin main
```

Vercel will:
1. Detect the push
2. Build the project
3. Run tests (if configured)
4. Deploy to production

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Issues**: https://github.com/DevGruGold/XMRT-DAO-Ecosystem/issues
- **Community**: Join our mesh network discussions

---

**Built with ⚡ by the XMRT-DAO community**
