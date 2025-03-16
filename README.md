# Vue-Flask-SaaS Quickstart

A complete starter template for building SaaS applications with Vue 3, Flask, and Supabase authentication.

## Overview

This template provides everything you need to quickly launch a SaaS product:

- **Frontend**: Vue 3 with TypeScript, Vite, Tailwind CSS, and dark/light mode
- **Backend**: Flask Python API with a structured project setup
- **Authentication**: Complete Supabase auth system with login, registration, and profile management
- **Infrastructure**: Development environment with concurrent frontend and backend servers

## Features

- **Authentication System**: Complete Supabase authentication with:
  - Email/password login and registration
  - User profile management
  - Protected routes and navigation guards
  - Session persistence across page refreshes

- **Dashboard Layout**: Professional SaaS dashboard with:
  - Responsive sidebar navigation
  - User profile section
  - Dark/light mode support
  - Mobile-friendly design

- **Landing Page**: Customizable landing page with:
  - Hero section with call-to-action buttons
  - Features showcase
  - Responsive navigation

- **Development Setup**: Streamlined development with:
  - Concurrent frontend and backend servers

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm (v7 or higher)
- Python 3.8 or higher
- pip (Python package installer)
- Supabase account and project (for authentication)

### Supabase Setup

1. Create a new project on [Supabase](https://supabase.com)
2. Enable Email Auth in Authentication settings
3. Copy your project URL and anon key from the API settings

### Environment Setup

1. Create a `.env` file in the frontend directory with your Supabase credentials:
```
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/brebribre/vue-flask-saas-quickstart.git
cd vue-flask-saas-quickstart
```

2. Install all dependencies (frontend and backend):
```bash
npm run install-all
```

This will:
- Install npm packages for the root project
- Install npm packages for the frontend
- Create a Python virtual environment in the backend directory
- Install Python dependencies from requirements.txt

### Development

To run both frontend and backend in development mode:
```bash
npm run dev
```

This will start:
- Frontend on http://localhost:5173
- Backend on http://localhost:5000 (default Flask port)

To run only frontend:
```bash
npm run frontend
```

To run only backend:
```bash
npm run backend
```

### Manual Backend Setup (if needed)

If you prefer to set up the backend manually or if the automatic setup fails:

1. Create and activate virtual environment:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run Flask:
```bash
flask run
```

### Production

1. Build the frontend:
```bash
npm run build
```

2. Start the production server:
```bash
npm start
```

## Authentication

The application uses Supabase for authentication:

- **Email/Password Authentication**: Users can register and login with email and password
- **User Profiles**: User metadata is stored in Supabase user profiles
- **Protected Routes**: Certain routes require authentication
- **Session Persistence**: Authentication state is maintained across page refreshes

## Project Structure

```
vue-flask-saas-quickstart/
├── frontend/         # Vue 3 frontend application
│   ├── src/          # Source code
│   │   ├── components/  # Reusable components
│   │   ├── views/       # Page components
│   │   ├── stores/      # Pinia stores (including auth)
│   │   ├── router/      # Vue Router configuration
│   │   └── lib/         # Utilities and libraries
├── backend/         # Flask Python backend application
│   ├── venv/        # Python virtual environment
│   └── requirements.txt  # Python dependencies
├── package.json     # Root package.json for running both services
└── README.md       # This file
```

## Available Scripts

- `npm run dev` - Run both frontend and backend in development mode
- `npm run frontend` - Run only frontend in development mode
- `npm run backend` - Run only backend in development mode (activates venv and runs Flask)
- `npm run install-all` - Install dependencies for both frontend and backend (including Python venv setup)
- `npm run build` - Build frontend for production
- `npm start` - Start the production server (Flask backend)

## Customization

### Frontend

- Update the landing page content in `frontend/src/views/HomeView.vue`
- Modify the navigation in `frontend/src/components/HomeNavbar.vue`
- Customize the dashboard in `frontend/src/views/DashboardView.vue`
- Add new routes in `frontend/src/router/index.ts`

### Backend

- Add new API endpoints in the `backend/routes/` directory
- Configure database models in `backend/models/`
- Update API documentation in Swagger annotations

## Notes

- The backend uses a Python virtual environment (venv) to manage dependencies
- Make sure to have Python and pip installed before running the installation
- If you're on Windows, you'll need to modify the scripts in package.json to use the appropriate commands for activating the virtual environment
- The Flask backend runs on port 5000 by default
- The frontend uses Supabase for authentication, ensure your Supabase project is properly configured
- User authentication state is maintained across page refreshes

## License

MIT