

## AL-ULOOM ACADEMY
## Software Requirements
## Specification
Al-Uloom Online Islamic Academy Management Portal
## Version: 1.0
## Date: April 2026
Status: Draft for Approval
Page 1 of 13

## 1. Introduction
## 1.1 Purpose
This document specifies the functional and non-functional requirements for the Al-Uloom Online
Islamic Academy Management Portal — a Learning Management System (LMS) supporting both live
virtual classrooms and self-paced recorded courses, with role-based access, automated
assessments, certificate issuance, moderated communications, and bulk email capability.
## 1.2 Scope
The system is a multi-role web application delivered as a Progressive Web App (PWA), allowing: -
Owner/Admin to manage the entire academy operations - Teachers to conduct live classes and share
learning materials - Students to attend live sessions, consume recorded content, attempt MCQs,
progress through modules, and earn certificates
## 1.3 Definitions
TermDefinition
PWAProgressive Web App — installable, offline-capable web application
LMSLearning Management System
SFUSelective Forwarding Unit — WebRTC media server pattern used by LiveKit
MCQMultiple Choice Question
RBACRole-Based Access Control
MinIOSelf-hosted, S3-compatible object storage
1.4 Technology Stack (Confirmed)
LayerChoice
FrontendNext.js (React) with PWA support, trilingual i18n (EN/AR/UR, RTL)
BackendDjango + Django REST Framework (DRF)
Real-time chatDjango Channels (WebSocket)
Async / Scheduled jobsCelery + Celery Beat + Redis broker
DatabasePostgreSQL 16
Object storageMinIO (self-hosted, S3-compatible)
Software Requirements SpecificationAl-Uloom Academy Portal
Page 2 of 13

LayerChoice
Live videoLiveKit (self-hosted SFU) + LiveKit Egress (recording)
Email — transactionalAmazon SES via SMTP
Email — bulk campaignsListmonk (self-hosted) + SES relay
HostingSelf-hosted VPS (Hetzner/DigitalOcean)
Reverse proxy / TLSNginx + Let's Encrypt
CDN / WAFCloudflare (free tier)
CI/CDGitHub Actions + Docker Compose deploys
ContainerizationDocker + Docker Compose
## 2. Overall Description
## 2.1 Product Perspective
The portal is a standalone web application. It integrates with: - A payment gateway (Stripe or
Razorpay) for optional online payment links - Amazon SES for email deliverability - Self-hosted
LiveKit for real-time video/audio
2.2 User Classes and Characteristics
Owner — Full system control, one or two accounts. Business decision authority. Can perform any
action including irreversible ones (after confirmation).
Admin — Day-to-day operations team. Can create courses and sessions, manage enrollments,
grant/revoke recording access, manage uploads, moderate messages, run email campaigns, and
manage users. Cannot delete courses or sessions.
Teacher (Presenter) — Subject-matter experts. Can start scheduled sessions at any time after the
scheduled date, start unscheduled sessions within their assigned courses, share learning materials,
and message students (within course context only — never privately, all chats visible to Admin/
Owner). Cannot stop recordings, chat privately, or manage the platform.
Student — End learners. Can enroll in multiple courses, attend live sessions, consume recorded
content, attempt MCQs, message their teacher (course-scoped, moderated), download permitted
recordings, and earn certificates.
## 2.3 Operating Environment
Modern evergreen browsers (Chrome, Firefox, Safari, Edge) — last 2 versions•
Software Requirements SpecificationAl-Uloom Academy Portal
Page 3 of 13

Installable as PWA on Android, iOS, desktop
Responsive: mobile (≥360 px), tablet, desktop
Trilingual UI: English, Arabic (RTL), Urdu (RTL)
2.4 Design and Implementation Constraints
All critical components must be FOSS-preferred where practical
Data sovereignty: all recordings, chat logs, user data stored on infrastructure controlled by the
academy
Concurrency target (Year 1): 100–500 registered students; up to 30 concurrent live sessions;
up to 500 concurrent users
Chat moderation is non-negotiable: every teacher–student message is persisted and visible to
Admin/Owner
2.5 Assumptions and Dependencies
Academy will provide domain names, SSL contact email, and SES sandbox exit
Academy will provide a bank account for payment gateway onboarding
Academy will assign a project point-of-contact available for weekly demos
VPS specs: minimum 8 vCPU / 16 GB RAM / 500 GB NVMe for application tier; separate
media node for LiveKit (8 vCPU / 16 GB / 1 Gbps network)
## 3. Functional Requirements
3.1 Authentication & Authorization (FR-AUTH)
IDRequirement
## FR-
## AUTH-01
Users authenticate via email + password. Passwords hashed with Argon2id
## FR-
## AUTH-02
Session management via JWT (15-min access token + 7-day refresh token, httpOnly
cookie)
## FR-
## AUTH-03
Passwords: min 10 chars, at least 1 letter, 1 number, 1 special char
## FR-
## AUTH-04
Forgot-password flow: time-limited (30 min) signed reset link emailed via SES
## FR-
## AUTH-05
Account lockout: 5 failed attempts → 15-min lockout; logged for admin
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
Software Requirements SpecificationAl-Uloom Academy Portal
Page 4 of 13

IDRequirement
## FR-
## AUTH-06
Optional 2FA (TOTP) for Owner and Admin roles (Phase 2)
## FR-
## AUTH-07
RBAC enforced at API layer; role permissions loaded from DB, not hard-coded
## FR-
## AUTH-08
Session revocation: Admin can force-logout any user
3.2 User & Role Management (FR-USR)
IDRequirement
FR-USR-01Admin can create, edit, deactivate users and assign a single role
FR-USR-02Owner can assign/revoke Admin role
FR-USR-03Bulk user import via CSV (email, name, phone, role, language)
FR-USR-04Each user has profile: full name, email, phone, language preference, timezone, avatar
FR-USR-05Students can have optional guardian email stored for group emails
FR-USR-06Audit log of who created/modified each user
3.3 Course Management (FR-CRS)
IDRequirement
## FR-
## CRS-01
Admin can create Live and Recorded course types
## FR-
## CRS-02
Each course has: title (trilingual), description (trilingual), thumbnail, price, assigned teacher,
status (draft/published/archived)
## FR-
## CRS-03
Admin and Owner can publish/unpublish courses
## FR-
## CRS-04
Admin cannot delete courses; only Owner can (with confirmation)
## FR-
## CRS-05
Recorded courses contain ordered Modules; each module contains media (video/audio),
PDFs, reference images, and exactly one MCQ quiz
## FR-
## CRS-06
Live courses contain scheduled sessions and optional shared learning materials
## FR-
## CRS-07
Course listing filtered by role: Admin/Owner see all; Teacher sees assigned; Student sees
enrolled
Software Requirements SpecificationAl-Uloom Academy Portal
Page 5 of 13

3.4 Live Sessions (FR-LIVE)
IDRequirement
## FR-
## LIVE-01
Admin schedules sessions with date/time/duration; system creates a LiveKit room identifier in
advance
## FR-
## LIVE-02
Teacher sees a "Start Session" button for any scheduled session assigned to them. Button is
enabled at any time after scheduling — supporting the "start off-schedule" requirement
## FR-
## LIVE-03
On start: system creates/joins the LiveKit room, issues a publisher JWT to the teacher, and
automatically initiates LiveKit Egress recording (RoomComposite)
## FR-
## LIVE-04
Students enrolled in the course see a "Join" button when the session goes live
## FR-
## LIVE-05
Attendance (join/leave timestamps) recorded automatically
## FR-
## LIVE-06
Teacher cannot stop or manipulate recording. Egress is stopped automatically when the room
empties or when session is marked ended
## FR-
## LIVE-07
Recordings uploaded to MinIO by LiveKit Egress; webhook creates a Recording DB record
## FR-
## LIVE-08
If the scheduled start time passes without teacher joining, the session is auto-flagged "Missed"
after a configurable grace period (default 30 min)
3.5 Recordings & Access Control (FR-REC)
IDRequirement
FR-REC-01All recordings are accessible to Owner and Admin by default
FR-REC-02Teachers and Students have no access to recordings unless explicitly granted
FR-REC-03Admin can grant recording access per-user or per-recording
FR-REC-04Admin can revoke access at any time
FR-REC-05Recording downloads use signed, short-lived URLs (default 1 hour)
FR-REC-06Admin can delete recordings; deletion removes DB record + storage object
FR-REC-07All access grant/revoke actions logged with actor and timestamp
Software Requirements SpecificationAl-Uloom Academy Portal
Page 6 of 13

3.6 Recorded Courses & MCQ Gating (FR-REC-LMS)
IDRequirement
## FR-REC-
## LMS-01
Each module contains: video (or audio or both), optional PDFs, optional images, exactly
one MCQ quiz
## FR-REC-
## LMS-02
MCQ quiz builder supports: unlimited questions, 2–6 options per question, exactly one
correct answer, optional time limit
## FR-REC-
## LMS-03
Student must attempt the quiz to proceed; no skipping
## FR-REC-
## LMS-04
Passing threshold is 40% by default, configurable per module
## FR-REC-
## LMS-05
On pass: next module unlocks immediately; progress persisted
## FR-REC-
## LMS-06
On fail: unlimited re-attempts allowed (unless max_attempts configured)
## FR-REC-
## LMS-07
Each attempt stored with answers, score, pass/fail, timestamp
## FR-REC-
## LMS-08
Question and option order is shuffled per attempt to deter screenshot sharing
## FR-REC-
## LMS-09
On completing all modules, a Certificate is auto-generated and emailed
3.7 Certificates (FR-CERT)
IDRequirement
## FR-
## CERT-01
Certificate PDF generated via WeasyPrint from HTML template
## FR-
## CERT-02
Contains: student full name, course title, issue date, unique certificate ID (UUID short form),
course duration, signatures (academy seal + owner signature image), QR code
## FR-
## CERT-03
QR code links to a public verification URL: /verify/{cert_id} showing issue status
## FR-
## CERT-04
Each certificate has a SHA-256 verification hash derived from (cert_id + student_id +
course_id + issued_at); stored alongside record
## FR-
## CERT-05
Student receives an email with download link on issuance
## FR-
## CERT-06
Admin can re-issue, revoke, or download any certificate
Software Requirements SpecificationAl-Uloom Academy Portal
Page 7 of 13

IDRequirement
## FR-
## CERT-07
Certificate rendered in student's preferred language (EN/AR/UR)
3.8 Messaging (FR-MSG)
IDRequirement
## FR-
## MSG-01
Messaging is scoped to a course room — one room per course (teacher + all enrolled
students)
## FR-
## MSG-02
No private/direct messaging between users — ever
## FR-
## MSG-03
Messages support: text, images (≤10 MB), documents (≤25 MB), audio notes (≤15 MB), links
with auto-preview
## FR-
## MSG-04
Real-time delivery via Django Channels (WebSocket)
## FR-
## MSG-05
All messages persisted; no ephemeral/disappearing messages
## FR-
## MSG-06
Admin Moderation Inbox: searchable, filterable (by course, user, date range, keyword); all
conversations visible
## FR-
## MSG-07
Admin can flag, hide, or export any conversation
## FR-
## MSG-08
Students and teachers see a banner: "This chat is moderated by the academy"
3.9 Shared Content in Live Sessions (FR-SHARE)
IDRequirement
## FR-
## SHARE-01
Teacher can upload homework/assignments before, during, or after a session
## FR-
## SHARE-02
Students can upload their work/submissions to the course
## FR-
## SHARE-03
Supported types: text files, videos (≤500 MB), audio files (≤100 MB), PDFs (≤50 MB),
external links
## FR-
## SHARE-04
Content tagged with course + session (if applicable) + uploader
Software Requirements SpecificationAl-Uloom Academy Portal
Page 8 of 13

IDRequirement
## FR-
## SHARE-05
Admin can view, download, and delete any shared content
3.10 Enrollment & Payments (FR-ENR)
IDRequirement
## FR-
## ENR-01
Admin can manually enroll a student in a course (status=ACTIVE immediately)
## FR-
## ENR-02
Admin can generate a course-specific payment link; enrollment sits in PENDING_PAYMENT
until payment webhook confirms
## FR-
## ENR-03
Payment gateway: Stripe (international) and/or Razorpay (India)
## FR-
## ENR-04
On successful payment webhook (verified via signature), enrollment → ACTIVE; welcome
email sent
## FR-
## ENR-05
Admin can revoke enrollment; user loses access but history is retained
## FR-
## ENR-06
Payment records immutable; refunds recorded as separate entries
## FR-
## ENR-07
Welcome email includes: login credentials (temporary password if newly created) + course
access instructions + portal URL
3.11 Bulk Email (FR-MAIL)
IDRequirement
## FR-
## MAIL-01
Admin composes campaigns in Listmonk with subject, HTML/plain body, and template
variables ({{name}}, etc.)
## FR-
## MAIL-02
Recipient lists: all users, all students, parents/guardians, students in a course, custom CSV
## FR-
## MAIL-03
Emails sent individually (one per recipient) via SES — never via CC/BCC-to-all. Each
recipient sees only their own address
## FR-
## MAIL-04
Campaigns support scheduling and pause/resume
## FR-
## MAIL-05
Delivery reports: sent, delivered, bounced, opened (via SES event feedback)
Software Requirements SpecificationAl-Uloom Academy Portal
Page 9 of 13

IDRequirement
## FR-
## MAIL-06
Unsubscribe link included in every bulk email (legal compliance)
## FR-
## MAIL-07
Transactional emails (password reset, enrollment, certificate) go directly via Django → SES,
not Listmonk
3.12 Admin Dashboard (FR-DASH)
IDRequirement
## FR-
## DASH-01
Overview metrics: active students, active courses, upcoming sessions today, recent
enrollments, monthly revenue
## FR-
## DASH-02
Recent activity feed: enrollments, session starts, certificate issuance, flagged messages
## FR-
## DASH-03
Storage usage meter (MinIO bucket sizes)
## FR-
## DASH-04
Audit log search
3.13 Internationalization (FR-I18N)
IDRequirement
## FR-
## I18N-01
UI fully translated: English, Arabic, Urdu
## FR-
## I18N-02
RTL layout support for Arabic and Urdu (mirrored navigation, text alignment)
## FR-
## I18N-03
Per-user language preference persisted; UI switches on login
## FR-
## I18N-04
Date/time formatting respects user timezone + locale
## FR-
## I18N-05
Content (course titles, descriptions) stored per language; fallback to English if translation
missing
## FR-
## I18N-06
Certificate template renders in student's language
Software Requirements SpecificationAl-Uloom Academy Portal
Page 10 of 13

- Non-Functional Requirements
## 4.1 Performance
API p95 response time ≤ 400 ms under normal load (100 concurrent requests)
Page LCP ≤ 2.5 s on 4G mobile
Live session join latency ≤ 3 s after clicking Join
Support 500 concurrent users; 30 concurrent live sessions; 100 concurrent WebSocket
connections
## 4.2 Security
HTTPS everywhere (Let's Encrypt); TLS 1.2 minimum
Passwords hashed with Argon2id (memory_cost=65 MB, time_cost=3, parallelism=4)
Rate limiting on auth endpoints: 5 requests / 15 min / IP (django-ratelimit)
CSRF protection on all state-changing endpoints
Strict Content-Security-Policy headers
All secrets in environment variables, never in code; managed via HashiCorp Vault or Doppler
(Phase 2) or .env files with restricted permissions (MVP)
Database backups: daily snapshots, 30-day retention, tested restore quarterly
Security updates applied within 7 days for critical CVEs
## 4.3 Privacy & Compliance
GDPR-aligned data handling: right to access, right to deletion within 30 days
Data export: user can request full data export (JSON)
No third-party tracking scripts on student-facing pages
Moderation disclosed in Terms of Service and visible in chat UI
## 4.4 Availability
99.5% uptime SLA target (excluding scheduled maintenance, ≤ 4 hours/month)
Scheduled maintenance windows announced 72 hours in advance
Graceful degradation: if LiveKit is down, recorded content still accessible
## 4.5 Scalability
Horizontal scalability: Django app stateless behind Nginx; scale by adding containers
LiveKit supports clustering if needed in future
MinIO supports distributed mode if storage needs grow
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
Software Requirements SpecificationAl-Uloom Academy Portal
Page 11 of 13

## 4.6 Usability
Accessible to WCAG 2.1 AA standard
Mobile-first responsive design
Intuitive role-specific landing dashboards
PWA installable; works offline for already-loaded recorded content (where permitted)
## 4.7 Maintainability
Code in single monorepo with clear separation of backend/frontend
Automated tests: ≥70% coverage on backend; critical flows tested end-to-end (Playwright)
Docker Compose for reproducible local development
Comprehensive README + architecture docs + runbooks for common ops (backup, restore,
scale)
## 4.8 Observability
Structured JSON logs shipped to a central log store (Loki + Grafana, self-hosted)
Metrics: Prometheus + Grafana dashboards (app, DB, LiveKit, storage)
Error tracking: GlitchTip (FOSS Sentry alternative)
Uptime monitoring: Uptime Kuma (FOSS)
## 5. System Interfaces
## 5.1 External Interfaces
LiveKit Server — gRPC + WebSocket for room mgmt, egress control, token issuance
Amazon SES — SMTP (port 587, STARTTLS) for email delivery; HTTPS webhook for
bounces/complaints
Listmonk — REST API for campaign creation; sends via SES relay
Stripe/Razorpay — REST API + signed webhooks for payments
## 5.2 Internal Interfaces
Django ↔ PostgreSQL (psycopg 3)
Django ↔ Redis (redis-py — used for Celery broker, Channels layer, cache)
Django ↔ MinIO (boto3, S3-compatible endpoint)
Next.js ↔ Django (REST over HTTPS)
Next.js ↔ Django Channels (WSS)
Next.js ↔ LiveKit (LiveKit JS SDK, WSS + WebRTC)
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
Software Requirements SpecificationAl-Uloom Academy Portal
Page 12 of 13

## 6. Data Retention & Deletion Policy
Data TypeRetention
User accountsUntil deletion requested; 30-day grace period then hard delete
Chat messages2 years minimum (moderation/audit)
Live session recordings1 year default; configurable per course
CertificatesPermanent (core academic record)
Payment records7 years (tax compliance)
Audit logs2 years
Email campaign logs1 year
- Out-of-Scope (MVP v1)
The following are deliberately deferred to Phase 2 to protect the 12-week timeline: - Mobile native
apps (PWA serves this need for MVP) - Advanced analytics / BI dashboards - Gamification (badges,
leaderboards, streaks) - Live class breakout rooms - Whiteboard / collaborative drawing in live class -
Parent portal (separate login for guardians) - TOTP 2FA - Multi-tenant (multiple academies on same
instance) - Automated transcription/captions on recordings - Forum / discussion boards - In-app
notifications (beyond email) — push notifications deferred
## 8. Acceptance Criteria Summary
The system is considered ready for production launch when: 1. All functional requirements marked
MVP have been implemented and tested 2. 30 concurrent live sessions sustained for 2 hours in load
test with recording 3. Penetration test completed with no Critical or High findings open 4. UAT sign-off
obtained from Owner across all 4 roles 5. Backup + restore drill executed successfully 6. Runbook
and admin user guide delivered 7. Trilingual UI validated by native speakers of Arabic and Urdu
End of SRS Document
Software Requirements SpecificationAl-Uloom Academy Portal
Page 13 of 13