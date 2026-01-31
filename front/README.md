# Todo Dashboard Frontend

A modern task management application built with Next.js 16+, TypeScript, Tailwind CSS, and Better Auth.

## Features

- User authentication (Sign up, Sign in, Sign out)
- Task management (Create, Read, Update, Delete)
- Task filtering by status (All, Pending, Completed)
- Task statistics and completion rate
- Responsive design for desktop and mobile
- Optimistic UI updates

## Tech Stack

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth
- **State Management**: React Query
- **UI Components**: Headless UI, Custom components

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the `front` directory
3. Install dependencies:

```bash
npm install
```

### Environment Variables

Create a `.env.local` file in the root of the `front` directory with the following variables:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8080
BETTER_AUTH_SECRET=your-secret-key-change-in-production
DATABASE_URL=sqlite://./sqlite.db
```

### Running the Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

### Building for Production

```bash
npm run build
npm run start
```

## Project Structure

```
front/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Authentication routes
│   │   ├── signin/
│   │   └── signup/
│   ├── dashboard/         # Protected dashboard route
│   ├── layout.tsx         # Root layout with AuthProvider
│   └── page.tsx           # Home page (redirects based on auth)
├── components/            # Reusable UI components
│   ├── auth/              # Authentication components
│   ├── task/              # Task management components
│   ├── ui/                # Base UI components
│   └── layout/            # Layout components
├── lib/                   # Utilities and API clients
├── hooks/                 # Custom React hooks
├── types/                 # TypeScript type definitions
└── public/                # Static assets
```

## API Integration

The frontend connects to a backend API for data persistence. The API client is configured in `lib/api.ts` and supports both real API calls and mock API for development.

## Authentication

Authentication is handled through Better Auth. The auth context is provided at the root layout level through the `AuthProvider`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Deployment

### Vercel Deployment

This application is designed for deployment on Vercel. The repository follows a monorepo structure with the Next.js frontend located in the `front/` directory.

#### Configuration

The deployment is configured with a `vercel.json` file in the repository root:

```json
{
  "framework": "nextjs",
  "root": "./front"
}
```

This tells Vercel to:
- Recognize the project as a Next.js application
- Use the `./front` directory as the project root
- Apply Next.js-specific build optimizations

#### Deployment Steps

1. Connect your GitHub repository to Vercel
2. Vercel will automatically detect the Next.js framework
3. The build command will run from the `front/` directory
4. All path aliases and dependencies will be resolved correctly

#### Common Issues Fixed

- **Path Resolution**: The root `vercel.json` file ensures proper path resolution for imports like `@/*`
- **Tailwind CSS**: Proper configuration with the new Tailwind engine (v4+)
- **Build Commands**: Simplified to use Next.js automatic detection instead of custom commands

## License

[Specify your license here]
