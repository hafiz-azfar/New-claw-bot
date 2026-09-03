# Al-Uloom Academy Management Portal 🚀

> **The Zoom & MS Teams Killer** - A self-hosted, privacy-first Learning Management System with enterprise-grade live video conferencing.

## 💪 Why Al-Uloom Beats Zoom/Teams/Wise

| Feature | Al-Uloom | Zoom | MS Teams |
|---------|----------|------|----------|
| **Cost** | Free (self-hosted) | $15/host/month | $6/user/month |
| **Session Duration** | Unlimited | 40 min (free) | 60 min (free) |
| **Participants** | 100+ (scalable) | 100 | 300 |
| **Auto-Recording** | ✅ Always | ❌ Paid only | ⚠️ Limited |
| **Data Sovereignty** | ✅ Your server | ❌ Cloud | ❌ Cloud |
| **LMS Integration** | ✅ Built-in | ❌ Separate | ⚠️ Complex |
| **Moderated Chat** | ✅ Built-in | ⚠️ Limited | ⚠️ Limited |
| **MCQ Quizzes** | ✅ During class | ❌ No | ❌ No |
| **Attendance Tracking** | ✅ Automatic | ⚠️ Manual | ⚠️ Manual |
| **Certificate Auto-Issue** | ✅ Built-in | ❌ No | ❌ No |
| **Multi-language (RTL)** | ✅ EN/AR/UR | ⚠️ Limited | ⚠️ Limited |

## 📋 Project Overview

Al-Uloom Academy is a self-hosted educational platform featuring:
- **LiveKit-Powered Video** - Superior to Zoom with <500ms latency
- **Role-Based Access Control** (Owner, Admin, Teacher, Student)
- **MCQ-based Progress Gating** (40% pass threshold for recorded courses)
- **Moderated Course Messaging** (no private chats, full audit trail)
- **Auto-Recording to MinIO** - Own your data, no cloud fees
- **Certificate Generation** with public verification
- **Multi-language Support** (English, Arabic, Urdu with RTL)
- **Payment Integration** (Stripe & Razorpay)
- **Email Campaigns** via Listmonk

## 🏗️ Architecture

### Backend (Django 5.0)
```
backend/aluloom/
├── apps/
│   ├── users/          # Authentication & RBAC (JWT, Argon2id)
│   ├── courses/        # Course & LMS management
│   ├── messaging/      # WebSocket chat & moderation
│   ├── payments/       # Stripe & Razorpay integration
│   ├── certificates/   # PDF certificate generation
│   ├── recordings/     # LiveKit recording management
│   ├── enrollments/    # Student enrollments
│   ├── live_sessions/  # 🎥 Live class management (Zoom killer)
│   ├── dashboard/      # Analytics & reporting
│   └── email_campaigns/# Listmonk integration
├── tasks/              # Celery background tasks
└── aluloom/            # Django settings & routing
```

### Infrastructure (Self-Hosted)
```
docker-compose.yml
├── PostgreSQL 16       # Primary database
├── Redis 7             # Cache, broker, Channels layer
├── MinIO               # S3-compatible object storage
├── LiveKit             # SFU for live video (Zoom alternative)
├── Django              # Application server
├── Celery Worker       # Async tasks
├── Celery Beat         # Scheduled tasks
└── Nginx               # Reverse proxy + TLS
```

### Frontend (React + Vite + PWA)
```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Route pages
│   ├── services/       # API services
│   ├── store/          # State management (Redux/Zustand)
│   ├── hooks/          # Custom React hooks
│   ├── locales/        # i18n translations (EN/AR/UR)
│   └── styles/         # Tailwind CSS + RTL support
└── public/             # Static assets
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- 8GB+ RAM recommended for LiveKit

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/hafiz-azfar/New-claw-bot.git
cd New-claw-bot
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
# IMPORTANT: Change all default passwords!
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Run migrations**
```bash
docker-compose exec backend python manage.py migrate
```

5. **Create superuser (Owner account)**
```bash
docker-compose exec backend python manage.py createsuperuser
```

6. **Access the application**
- API: http://localhost:8000/api/v1/
- Swagger Docs: http://localhost:8000/api/docs/
- MinIO Console: http://localhost:9001
- Admin Panel: http://localhost:8000/admin/

## 📦 Services

| Service | Port | Description |
|---------|------|-------------|
| Django API | 8000 | Main REST API server |
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Cache, Celery broker, Channels |
| MinIO | 9000 | S3-compatible object storage |
| MinIO Console | 9001 | Web UI for MinIO |
| LiveKit | 7880 | SFU for live video |
| LiveKit RTC | 7881 | WebRTC traffic |
| Nginx | 80/443 | Reverse proxy |

## 🔑 Key Features

### 🎥 Live Sessions (Beat Zoom)
- **One-Click Start** - Teacher can start any time after scheduled date
- **Auto-Recording** - Every session recorded to MinIO automatically
- **Unlimited Duration** - No 40-minute limit
- **Low Latency** - <500ms with SFU architecture
- **Attendance Tracking** - Automatic join/leave logging
- **Role-Based Tokens** - Different permissions for teacher/student
- **Moderated Chat** - All messages visible to admins

### 📚 Recorded Courses
- **Module-Based Structure** - Organized learning paths
- **MCQ Gating** - Must score 40% to proceed
- **Multiple Content Types** - Video, audio, PDF, images
- **Progress Tracking** - Per-student completion stats

### 👥 User Management
- **4 Roles**: Owner (full control), Admin (operations), Teacher (presenter), Student (learner)
- **JWT Authentication** - Secure token-based auth
- **Password Reset** - Email-based recovery
- **Audit Logging** - Track all admin actions
- **Bulk Import** - CSV upload for users

### 💳 Payments
- **Stripe Integration** - Global payments
- **Razorpay** - India-specific payments
- **Webhook Handling** - Automatic enrollment on payment
- **Refund Management** - Admin-controlled refunds

### 📜 Certificates
- **Auto-Generation** - PDF certificates on course completion
- **Unique Hash** - Public verification endpoint
- **Trilingual** - Certificate in student's language

### 🌐 Internationalization
- **3 Languages**: English, Arabic (RTL), Urdu (RTL)
- **Per-User Preference** - Saved in profile
- **Content Translation** - Course titles/descriptions per language

## 📖 API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - Login (get JWT tokens)
- `POST /api/v1/auth/refresh/` - Refresh access token
- `POST /api/v1/auth/logout/` - Logout (blacklist token)
- `POST /api/v1/auth/password/reset/` - Request password reset
- `POST /api/v1/auth/password/reset/confirm/` - Reset password

### Live Sessions (Zoom Alternative)
- `GET /api/v1/sessions/` - List sessions (filtered by role)
- `POST /api/v1/sessions/` - Create session (admin only)
- `GET /api/v1/sessions/{id}/` - Get session details
- `POST /api/v1/sessions/{id}/start/` - Start session (teacher)
- `POST /api/v1/sessions/{id}/end/` - End session (teacher)
- `GET /api/v1/sessions/{id}/join_token/` - Get LiveKit join token
- `GET /api/v1/sessions/{id}/attendance/` - Get attendance records
- `GET /api/v1/sessions/upcoming/` - Get upcoming sessions
- `GET /api/v1/sessions/missed/` - Get missed sessions

### Courses
- `GET /api/v1/courses/` - List courses
- `POST /api/v1/courses/` - Create course (admin)
- `GET /api/v1/courses/{id}/` - Get course details
- `PUT /api/v1/courses/{id}/` - Update course
- `DELETE /api/v1/courses/{id}/` - Delete course (owner only)
- `POST /api/v1/courses/{id}/publish/` - Publish course
- `POST /api/v1/courses/{id}/unpublish/` - Unpublish course

### Messaging
- `WS /ws/chat/course/{id}/` - WebSocket for course chat
- `GET /api/v1/messages/course/{id}/` - Get course messages
- `POST /api/v1/messages/flag/` - Flag inappropriate message

### Certificates
- `GET /api/v1/certificates/` - List user's certificates
- `GET /api/v1/certificates/{id}/download/` - Download PDF
- `GET /api/v1/certificates/verify/{hash}/` - Public verification

## 🔒 Security Features

- **Argon2id Password Hashing** - Industry-leading security
- **JWT with Short Expiry** - 15-min access, 7-day refresh
- **Rate Limiting** - 5 attempts per 15 minutes on auth
- **CORS Protection** - Configurable allowed origins
- **Security Headers** - HSTS, CSP, X-Frame-Options
- **Audit Logging** - All admin actions tracked
- **Moderated Chats** - No private teacher-student messages
- **Data Sovereignty** - All data on your infrastructure

## 🛠️ Development

### Run migrations
```bash
docker-compose exec backend python manage.py migrate
```

### Create test data
```bash
docker-compose exec backend python manage.py shell
>>> from aluloom.apps.users.management.commands.create_test_data import Command
>>> Command().handle()
```

### Run tests
```bash
docker-compose exec backend pytest
```

### View logs
```bash
docker-compose logs -f backend
docker-compose logs -f livekit
```

## 📊 Performance Targets

- **API Response Time**: p95 ≤ 400ms
- **Page Load**: LCP ≤ 2.5s on 4G
- **Live Session Join**: ≤ 3s latency
- **Concurrent Users**: 500+ supported
- **Concurrent Sessions**: 30+ live rooms
- **Uptime SLA**: 99.5%

## 📝 License

MIT License - Self-hosted and free forever.

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines before submitting PRs.

## 📞 Support

For commercial support and custom development, contact: support@aluloom.academy

---

**Built with ❤️ for Islamic Education** | **Data Sovereignty Matters** | **Self-Hosted Freedom**
