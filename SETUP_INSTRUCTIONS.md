# Setup Instructions

## Setting Up Environment Variables

To get the application working locally, you need to set up your environment variables correctly.

### Backend Environment Variables (.env file)

1. Open the `.env` file in the root directory
2. Replace the placeholder values with your actual credentials:

```
# Supabase Configuration
SUPABASE_URL=your_actual_supabase_project_url_here
SUPABASE_KEY=your_actual_supabase_service_key_here

# OpenAI API Configuration (optional)
OPENAI_API_KEY=your_actual_openai_api_key_here

# Application Configuration
FRONTEND_URL=http://localhost:3000
```

### How to Get Your Supabase Credentials

1. Go to your Supabase project dashboard
2. Click on "Project Settings" → "API"
3. Copy the "Project URL" (this is your SUPABASE_URL)
4. Copy the "service_role" key (this is your SUPABASE_KEY)

### How to Get Your OpenAI API Key (Optional)

1. Go to platform.openai.com
2. Sign in to your account
3. Go to "API Keys"
4. Create a new secret key
5. Copy the key

### Security Reminder

⚠️ **Important**: Never commit these actual credentials to Git!
The `.env` file is already in `.gitignore` to prevent accidental commits.

### Starting the Application

After setting up your credentials:

1. Start the backend server:
   ```bash
   cd backend
   python server.py
   ```

2. In a new terminal, start the frontend:
   ```bash
   cd frontend
   npm start
   ```

3. Open your browser and go to http://localhost:3000

### Troubleshooting

If you're still having issues:

1. Make sure both the frontend and backend servers are running
2. Check that you're using the correct port numbers:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:5001
3. Verify your credentials are correct
4. Check the browser console for any error messages
5. Check the backend terminal for any error messages

### Verifying Everything Works

1. Go to http://localhost:3000
2. Click "Get Started"
3. Try to sign up or log in
4. You should be able to authenticate successfully