# Todo App - Running Instructions

This document provides instructions to run both the backend and frontend servers for the Todo application.

## Prerequisites

- Python 3.13+ installed
- Node.js 18+ installed
- npm or yarn installed

## Environment Setup

### Backend (Python FastAPI)
1. Navigate to the backend directory:
   ```bash
   cd Back-End
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Or install required packages manually:
   ```bash
   pip install fastapi uvicorn sqlmodel python-jose psycopg2-binary alembic python-multipart email-validator
   ```

3. Make sure your `.env` file in the `Back-End` directory contains the correct database configuration and secrets.

### Frontend (Next.js)
1. Navigate to the frontend directory:
   ```bash
   cd front
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Make sure your `.env` file in the `front` directory contains the correct API configuration.

## Running the Applications

### Method 1: Manual Start (Separate Terminals)

#### Start Backend Server:
1. Open a terminal/command prompt
2. Navigate to the backend directory:
   ```bash
   cd G:\Todo-app\Back-End
   ```
3. Run the backend server:
   ```bash
   uvicorn src.main:app --reload
   ```
   The backend will be available at: `http://localhost:8000`

#### Start Frontend Server:
1. Open another terminal/command prompt
2. Navigate to the frontend directory:
   ```bash
   cd G:\Todo-app\front
   ```
3. Run the frontend server:
   ```bash
   npm run dev
   ```
   The frontend will be available at: `http://localhost:3000` (or another available port)

### Method 2: Using Package Scripts (if available)

#### Start Backend:
```bash
cd G:\Todo-app\Back-End
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

#### Start Frontend:
```bash
cd G:\Todo-app\front
npm run dev
```

## Default Ports

- Backend API: `http://localhost:8000`
- Frontend App: `http://localhost:3000` (or first available port like 3001, 3002, etc.)

## Application Features

Once both servers are running:

1. **Landing Page**: `http://localhost:[FRONTEND_PORT]/landing-page`
2. **Sign In**: `http://localhost:[FRONTEND_PORT]/signin`
3. **Sign Up**: `http://localhost:[FRONTEND_PORT]/signup`
4. **Dashboard**: `http://localhost:[FRONTEND_PORT]/dashboard`

## Troubleshooting

### Common Issues:

1. **Port already in use**:
   - The application will automatically use the next available port
   - Check the terminal output for the actual port being used

2. **Environment variables not found**:
   - Make sure `.env` files are properly configured in both directories
   - Check that environment variables match between frontend and backend

3. **Database connection errors**:
   - Verify your database credentials in the backend `.env` file
   - Ensure your database server is running

4. **Frontend cannot connect to backend**:
   - Verify that the `NEXT_PUBLIC_API_BASE_URL` in frontend `.env` matches your backend URL
   - Ensure backend server is running before starting frontend

### Restart Steps:

If you need to restart the applications:
1. Stop both servers (Ctrl+C in each terminal)
2. Start backend server first
3. Wait for backend to be fully ready
4. Start frontend server

## Project Structure

```
Todo-app/
├── Back-End/                 # Python FastAPI backend
│   ├── src/
│   │   ├── main.py          # Main application entry point
│   │   ├── auth/            # Authentication modules
│   │   ├── api/             # API route definitions
│   │   ├── models/          # Database models
│   │   └── database.py      # Database configuration
│   └── .env                 # Backend environment variables
├── front/                   # Next.js frontend
│   ├── app/                 # App router pages
│   │   ├── landing-page/    # Landing page
│   │   ├── signin/          # Sign in page
│   │   ├── signup/          # Sign up page
│   │   └── dashboard/       # Dashboard page
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utility functions
│   └── .env                 # Frontend environment variables
└── RUN_INSTRUCTIONS.md      # This file
```