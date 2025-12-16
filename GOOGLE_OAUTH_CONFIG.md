# Google OAuth Configuration Guide

This guide explains how to configure Google OAuth for your Supabase project.

## Prerequisites

1. A Google Cloud Platform account
2. A Supabase project
3. Access to your Supabase dashboard

## Step 1: Create Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. Select "Web application" as the application type
6. Set the following values:
   - Name: `Executive Presence App`
   - Authorized JavaScript origins: `http://localhost:3000`
   - Authorized redirect URIs: `http://localhost:3000/auth/callback`
7. Click "Create"
8. Copy the Client ID and Client Secret (you'll need these later)

## Step 2: Configure Google OAuth in Supabase

1. Go to your Supabase dashboard
2. Navigate to "Authentication" > "Providers"
3. Find "Google" in the list of providers
4. Toggle the switch to enable Google authentication
5. Enter the following information:
   - Client ID: [Your Google OAuth Client ID]
   - Secret: [Your Google OAuth Client Secret]
6. Save the configuration

## Step 3: Test Google OAuth

1. Open your browser and go to http://localhost:3000
2. Click on "Get Started" to go to the login page
3. Click the "Sign in with Google" button
4. You should be redirected to Google's OAuth consent screen
5. After authentication, you should be redirected back to your application

## Troubleshooting

If you encounter issues:

1. Verify that the redirect URI in Google Cloud Console matches exactly with your application's callback URL
2. Check that the Supabase Google provider is properly configured with the correct Client ID and Secret
3. Ensure your environment variables are correctly set
4. Check the browser console for any JavaScript errors
5. Check the backend server logs for any authentication errors

## Production Deployment

For production deployment:

1. Add your production domain to the authorized JavaScript origins and redirect URIs in Google Cloud Console
2. Update the `FRONTEND_URL` environment variable to your production URL
3. Ensure HTTPS is used in production environments