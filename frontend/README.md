# Al-Uloom Frontend

React-based frontend for Al-Uloom Academy Management Portal - The Zoom/Teams Killer with integrated LMS.

## Tech Stack

- **React 18** with TypeScript
- **Vite** - Fast build tool
- **TailwindCSS** - Utility-first CSS
- **LiveKit Client** - Real-time video conferencing
- **Zustand** - State management
- **React Router** - Navigation
- **Axios** - HTTP client

## Features

### 🎥 Video Classroom (Zoom/Teams Competitor)
- HD video conferencing with LiveKit
- Auto-recording to self-hosted MinIO storage
- Teacher controls: mute all, screen share, recording toggle
- Student attendance tracking
- In-class MCQ quizzes overlay
- Moderated group chat
- Participant list with speaking indicators

### 📚 LMS Integration
- Course dashboard
- Module navigation
- Quiz attempts with 40% gating
- Certificate viewing

### 🔐 Authentication
- JWT-based auth
- Role-based access (Owner/Admin/Teacher/Student)
- Protected routes

## Setup

### Prerequisites
- Node.js 18+
- Backend running on `http://localhost:8000`
- LiveKit server running on `ws://localhost:7880`

### Installation

```bash
# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env with your configuration
# VITE_API_URL=http://localhost:8000/api
# VITE_LIVEKIT_URL=ws://localhost:7880

# Start development server
npm run dev
```

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── VideoClassroom/
│   │       ├── VideoRoom.tsx      # Main video grid
│   │       ├── ControlBar.tsx     # Teacher/student controls
│   │       ├── MCQOverlay.tsx     # Quiz interface
│   │       └── SidePanel.tsx      # Chat & participants
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   └── ClassroomPage.tsx
│   ├── services/
│   │   └── api.ts                 # API client
│   ├── store/
│   │   └── index.ts               # Zustand stores
│   ├── styles/
│   │   └── index.css              # Tailwind + custom
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.cjs
```

## Environment Variables

Create a `.env` file in the root:

```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
VITE_LIVEKIT_URL=ws://localhost:7880
```

## Demo Accounts

- **Teacher**: teacher@aluloom.com / demo123
- **Student**: student@aluloom.com / demo123

## Key Components

### VideoRoom
Main video conferencing component using LiveKit. Handles:
- Room connection
- Video grid layout (auto-adjusts for 1-50+ participants)
- Recording state
- MCQ overlay display

### ControlBar
Role-specific controls:
- **All users**: Mic/camera toggle, chat, participants
- **Teachers only**: Start/stop recording, launch quiz, mute all students

### MCQOverlay
Full-screen quiz interface:
- Countdown timer
- Multiple choice options
- Submit/skip functionality
- Auto-close after submission

### SidePanel
Toggle between:
- **Chat**: Moderated course chat with message history
- **Participants**: List of all attendees with speaking indicators

## API Integration

All API calls go through `src/services/api.ts` which provides:
- JWT token injection
- Automatic 401 handling (redirect to login)
- Typed service methods for:
  - `authService` - Login, logout, register
  - `courseService` - Courses, modules, quizzes
  - `liveSessionService` - Join sessions, get tokens, recording
  - `messagingService` - Chat history, send messages
  - `attendanceService` - View/export attendance

## State Management

Using Zustand for lightweight state:

- `useAuthStore` - User authentication state
- `useCourseStore` - Courses and modules
- `useLiveSessionStore` - Active session, recording, MCQ state
- `useUIStore` - Sidebar, chat, participants panel visibility

## Styling

Custom Tailwind theme with dark mode by default:
- Primary: Blue (#3b82f6)
- Background: Slate (#0f172a, #1e293b)
- Custom video grid layouts
- Responsive design

## Development Commands

```bash
# Start dev server
npm run dev

# Type check
npx tsc --noEmit

# Build production bundle
npm run build

# Preview production build
npm run preview

# Lint (if ESLint configured)
npm run lint
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

Requires WebRTC support for video conferencing.

## License

Proprietary - Al-Uloom Academy
