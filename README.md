# Stratigo AI Agent Platform

A platform for creating and managing AI agents that can connect with external software systems.

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm (v7 or higher)
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/brebribre/stratigo-job.git
cd stratigo-job
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

## Project Structure

```
stratigo-job/
├── frontend/         # React frontend application
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

## Notes

- The backend uses a Python virtual environment (venv) to manage dependencies
- Make sure to have Python and pip installed before running the installation
- If you're on Windows, you'll need to modify the scripts in package.json to use the appropriate commands for activating the virtual environment
- The Flask backend runs on port 5000 by default
- Make sure your backend's requirements.txt is up to date when adding new Python packages