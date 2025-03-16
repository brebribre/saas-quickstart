# SaaS Quickstart

A complete starter template for building SaaS applications with Vue 3 with shad-cn and Tailwind CSS, Flask, and Supabase authentication.

## Overview

This template provides everything you need to quickly launch a SaaS product:

- **Frontend**: Vue 3 with TypeScript, Vite, Tailwind CSS, and shad-cn
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

```
## Available Scripts

- `npm run dev` - Run both frontend and backend in development mode
- `npm run frontend` - Run only frontend in development mode
- `npm run backend` - Run only backend in development mode (activates venv and runs Flask)
- `npm run install-all` - Install dependencies for both frontend and backend (including Python venv setup)
- `npm run build` - Build frontend for production
- `npm start` - Start the production server (Flask backend)

## License

MIT
