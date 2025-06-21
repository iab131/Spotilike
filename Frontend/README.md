# Spotilike Frontend

This is the frontend for the Spotilike application - a Spotify-based player that detects user emotions and reactions to music.

## Features (UI Only)

- Spotify authentication
- Emotion/mood detection display interface
- Auto-adjusting volume based on distance
- Search functionality for finding songs by mood/emotion
- Curated playlists based on detected reactions
- Categorized music collections (calm, rap, throwbacks, etc.)

## Technology Stack

- Next.js (React framework)
- TypeScript
- TailwindCSS for styling

## Getting Started

### Prerequisites

- Node.js 16.x or later
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the front end directory

```bash
cd "front end"
```

3. Install dependencies

```bash
npm install
# or
yarn install
```

4. Start the development server

```bash
npm run dev
# or
yarn dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Deployment on Vercel

This project is designed to be deployed on Vercel. To deploy:

1. Push your code to a Git repository (GitHub, GitLab, or Bitbucket)
2. Import your repository on Vercel: https://vercel.com/import
3. Vercel will detect it's a Next.js project and set up the build configuration
4. Click "Deploy"

## Notes

- This is a UI-only implementation without actual functionality
- To implement functionality, you'll need to:
  - Connect to Spotify API for authentication and music control
  - Integrate with the facial recognition backend
  - Implement the distance detection for volume control
