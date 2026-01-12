# Deployment Guide for Render

This guide explains how to deploy the Warhammer Ranking System to Render.

## Prerequisites

1. A GitHub account with your code pushed to a repository
2. A Render account (sign up at https://render.com)
3. Your repository should be public or Render should have access to it

## Deployment Steps

### 1. Prepare Your Repository

Make sure you've committed and pushed all files, especially:
- `render.yaml` (in the root directory)
- All backend code in `backend/`
- All frontend code in `frontend/`

### 2. Create a New Blueprint on Render

1. Go to the [Render Dashboard](https://dashboard.render.com/)
2. Click **New** → **Blueprint**
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file

### 3. Configure Environment Variables

Render will automatically configure most environment variables from `render.yaml`, but you may need to manually add:

**Backend Service (warhammer-ranking-api)**:
- `DISCORD_TOKEN` - Your Discord bot token (if using Discord integration)
- `DISCORD_GUILD_ID` - Your Discord server ID (if using Discord integration)
- `SECRET_KEY` - Will be auto-generated, but you can override if needed

**Frontend Service (warhammer-ranking-frontend)**:
- `VITE_API_BASE_URL` - Will be auto-configured to point to your backend

### 4. Review and Deploy

1. Review the services that will be created:
   - **warhammer-ranking-api** (Web Service - Backend API)
   - **warhammer-ranking-frontend** (Static Site - React Frontend)
   - **warhammer-ranking-db** (PostgreSQL Database)

2. Click **Apply** to start the deployment

3. Wait for all services to build and deploy (usually 5-10 minutes)

### 5. Access Your Application

Once deployed, you'll have:
- **Frontend URL**: `https://warhammer-ranking-frontend.onrender.com`
- **Backend API URL**: `https://warhammer-ranking-api.onrender.com`
- **API Docs**: `https://warhammer-ranking-api.onrender.com/docs`

## Database Initialization

The database will be automatically initialized on first run. The backend service includes code to create all necessary tables.

## Custom Domain (Optional)

To add a custom domain:
1. Go to your frontend service settings
2. Navigate to **Custom Domains**
3. Add your domain and follow the DNS configuration instructions

## Monitoring

- **Logs**: View logs for each service in the Render Dashboard
- **Metrics**: Monitor CPU, memory, and bandwidth usage
- **Health Checks**: Backend service has a `/health` endpoint

## Troubleshooting

### Backend won't start
- Check the logs in the Render Dashboard
- Verify all environment variables are set correctly
- Ensure `DATABASE_URL` is connecting to the PostgreSQL database

### Frontend shows connection errors
- Check that `VITE_API_BASE_URL` points to the correct backend URL
- Verify CORS settings in the backend allow your frontend domain

### Database connection issues
- Verify the PostgreSQL database is running
- Check the internal connection string is being used
- Review database logs in the Render Dashboard

## Free Tier Limitations

If using Render's free tier:
- Services spin down after 15 minutes of inactivity
- First request after spin-down will be slower (cold start)
- 750 hours/month of running time
- Database limited to 1 GB storage

Consider upgrading to paid plans for production use.

## Updating Your Application

To deploy updates:
1. Push changes to your GitHub repository
2. Render will automatically detect changes and redeploy
3. Monitor the deployment progress in the dashboard

## Scaling

To scale your application:
1. Go to service settings in the Render Dashboard
2. Upgrade the instance type (from free to starter/standard/pro)
3. Enable autoscaling if needed
4. Increase database resources as your data grows

## Support

- Render Documentation: https://render.com/docs
- Community Forum: https://community.render.com/
- Status Page: https://status.render.com/
