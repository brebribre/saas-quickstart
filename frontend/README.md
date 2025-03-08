# Vue + Tailwind CSS + shadcn Project

This is a clean, modern web application template built with:

- Vue.js
- Vite
- Tailwind CSS
- shadcn components

## Features

- **Authentication**: Login and registration with email and Google OAuth
- **Dashboard**: Simple dashboard with sidebar navigation
- **Theme Switching**: Light and dark mode support
- **Responsive Design**: Works on all devices

## Getting Started

1. Clone the repository
2. Install dependencies:

```bash
cd frontend
npm install
```

3. Run the development server:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

- `src/components`: UI components
  - `auth`: Authentication-related components
  - `layout`: Layout components (sidebar, etc.)
  - `ui`: shadcn UI components
- `src/contexts`: React context providers
  - `AuthContext.tsx`: Authentication context
  - `ThemeContext.tsx`: Theme context
- `src/pages`: Application pages
  - `Login.tsx`: Login page
  - `Register.tsx`: Registration page
  - `Dashboard.tsx`: Dashboard page
  - `NotFound.tsx`: 404 page
- `src/integrations`: External service integrations
  - `supabase`: Supabase client and types

## Technologies

- **Vue.js**: Frontend framework
- **Vite**: Build tool
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn**: Unstyled, accessible UI components
- **Supabase**: Backend as a Service for authentication

## License

MIT
