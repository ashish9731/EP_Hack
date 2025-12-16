# Deployment Guide

This guide explains how to deploy the Executive Presence application to production environments.

## Architecture Overview

The application consists of two main components:
1. **Frontend**: React application that can be deployed to Vercel
2. **Backend**: Python FastAPI server that needs to be deployed separately

## Frontend Deployment (Vercel)

### Prerequisites
1. A Vercel account
2. The repository connected to Vercel

### Environment Variables
Set the following environment variables in your Vercel project settings:

```
REACT_APP_PROD_BACKEND_URL=https://your-backend-domain.com
```

Replace `https://your-backend-domain.com` with the actual URL of your deployed backend.

### Deployment Steps
1. Connect your GitHub repository to Vercel
2. Set the environment variables in Vercel dashboard
3. Deploy the application

## Backend Deployment Options

Since Vercel doesn't support long-running Python servers, you need to deploy the backend separately. Here are several options:

### Option 1: Render.com (Recommended for simplicity)

1. Create an account at [Render](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set the following configuration:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `uvicorn backend.server:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_key
     OPENAI_API_KEY=your_openai_key
     FRONTEND_URL=https://your-vercel-app.vercel.app
     ```

### Option 2: Railway.app

1. Create an account at [Railway](https://railway.app)
2. Create a new project
3. Connect your GitHub repository
4. Railway will automatically detect the Python application
5. Set the environment variables in the Railway dashboard

### Option 3: Heroku

1. Install the Heroku CLI
2. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```
3. Set environment variables:
   ```bash
   heroku config:set SUPABASE_URL=your_supabase_url
   heroku config:set SUPABASE_KEY=your_supabase_key
   heroku config:set OPENAI_API_KEY=your_openai_key
   heroku config:set FRONTEND_URL=https://your-vercel-app.vercel.app
   ```
4. Deploy:
   ```bash
   git push heroku main
   ```

### Option 4: AWS EC2 or Elastic Beanstalk

1. Launch an EC2 instance or create an Elastic Beanstalk application
2. Deploy the backend code
3. Set up the environment variables
4. Configure security groups to allow traffic on the appropriate port

## Environment Variables Required

Both frontend and backend require specific environment variables:

### Backend Environment Variables
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_key
OPENAI_API_KEY=your_openai_api_key
FRONTEND_URL=https://your-production-frontend-url
```

### Frontend Environment Variables (Vercel)
```
REACT_APP_PROD_BACKEND_URL=https://your-production-backend-url
```

## Supabase Configuration

Ensure your Supabase project is properly configured:

1. Enable email authentication
2. Enable Google OAuth (if using)
3. Configure redirect URLs in Supabase auth settings:
   - For development: `http://localhost:3000/auth/callback`
   - For production: `https://your-vercel-app.vercel.app/auth/callback`

## Google OAuth Setup

If using Google OAuth, you need to:

1. Set up OAuth credentials in Google Cloud Console
2. Add the credentials to your Supabase authentication settings
3. Configure the redirect URLs appropriately

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure your backend has the correct CORS configuration and that `FRONTEND_URL` is set correctly.

2. **Authentication Failures**: Check that Supabase credentials are correct and that the auth providers are enabled.

3. **API Connection Issues**: Verify that the `REACT_APP_PROD_BACKEND_URL` points to the correct backend URL.

### Testing the Deployment

1. After deployment, visit your frontend URL
2. Try to sign up or log in
3. Check the browser console for any errors
4. Verify that API calls are being made to the correct backend URL

## Monitoring and Maintenance

1. Monitor your backend logs for errors
2. Set up alerts for critical failures
3. Regularly update dependencies
4. Rotate API keys periodically