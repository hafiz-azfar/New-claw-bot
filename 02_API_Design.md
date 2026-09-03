

## AL-ULOOM ACADEMY
REST API Design
## Specification
Al-Uloom Online Islamic Academy Management Portal
## Version: 1.0
## Date: April 2026
Status: Draft for Approval
Page 1 of 15

## 1. Conventions
## 1.1 Request / Response Format
All requests and responses are JSON (Content-Type: application/json)
File uploads use multipart/form-data on designated endpoints only
All timestamps are ISO 8601 UTC: 2026-05-15T14:30:00Z
All IDs are UUIDv7 strings
## 1.2 Pagination
List endpoints support cursor-based pagination:
GET /api/v1/courses?limit=20&cursor=eyJpZCI6Ii4uLiJ9
Response includes:
## {
## "results": [...],
"next_cursor": "eyJpZCI6Ii4uLiJ9",
"has_more": true
## }
1.3 Error Format (RFC 7807 Problem Details)
## {
## "type": "https://aluloom.academy/errors/validation",
"title": "Validation failed",
## "status": 400,
"detail": "Email is already in use",
"errors": { "email": ["This email is already registered."] },
"trace_id": "01JBXYZ..."
## }
1.4 Standard HTTP Status Codes
CodeMeaning
## 200OK
201Created
## •
## •
## •
## •
REST API Design SpecificationAl-Uloom Academy Portal
Page 2 of 15

CodeMeaning
202Accepted (async job queued)
204No Content
400Bad Request / validation error
401Unauthenticated
403Forbidden (RBAC denial)
404Not Found
409Conflict
422Unprocessable Entity
429Rate Limited
500Server Error
## 1.5 Permissions Legend
SymbolWho
Public (unauthenticated)
Student
‍Teacher
⚙️Admin
Owner
## 2. Authentication & User
## 2.1 Auth
MethodEndpointPermDescription
POST/auth/loginLogin with email + password; returns access token + sets
refresh cookie
POST/auth/refreshExchange refresh cookie for new access token
POST/auth/logoutAllInvalidate refresh token
REST API Design SpecificationAl-Uloom Academy Portal
Page 3 of 15

MethodEndpointPermDescription
POST/auth/forgot-
password
Trigger reset email
POST/auth/reset-
password
Submit new password with reset token
POST/auth/change-
password
AllChange own password
Example: POST /auth/login
## // Request
{ "email": "teacher@aluloom.academy", "password": "P@ssw0rd!" }
## // Response 200
## {
"access_token": "eyJhbGci...",
"token_type": "Bearer",
## "expires_in": 900,
## "user": {
## "id": "019012ab-...",
## "email": "teacher@aluloom.academy",
"full_name": "Ustadh Ahmad",
## "role": "teacher",
## "language_pref": "en"
## }
## }
2.2 Current User (Me)
MethodEndpointPermDescription
GET/meAllCurrent user profile
PATCH/meAllUpdate own profile (name, phone, language, timezone,
avatar)
GET/me/courses‍Courses relevant to me (enrolled as student / teaching)
GET/me/sessions/
upcoming
‍My upcoming live sessions (next 7 days)
GET/me/certificatesMy earned certificates
REST API Design SpecificationAl-Uloom Academy Portal
Page 4 of 15

## 3. Users & Roles
MethodEndpointPermDescription
GET/users⚙️List users (filters: role, status, search)
POST/users⚙️Create user
GET/users/{id}⚙️User detail
PATCH/users/{id}⚙️Update user
POST/users/{id}/deactivate⚙️Deactivate user (soft)
POST/users/{id}/activate⚙️Reactivate user
POST/users/{id}/force-logout⚙️Revoke all refresh tokens
POST/users/import⚙️Bulk CSV import (multipart)
GET/roles⚙️List roles
Example: POST /users
## // Request
## {
## "email": "student1@example.com",
"full_name": "Aisha Khan",
## "phone": "+971501234567",
## "role": "student",
## "language_pref": "ur",
"timezone": "Asia/Karachi",
## "guardian_email": "parent@example.com"
## }
## // Response 201
## { "id": "019012ab-...", "email": "student1@example.com", ... ,
"temporary_password": "TempP@ss12" }
## 4. Courses & Modules
## 4.1 Courses
MethodEndpointPermDescription
GET/coursesAllList courses (filtered by role)
REST API Design SpecificationAl-Uloom Academy Portal
Page 5 of 15

MethodEndpointPermDescription
POST/courses⚙️Create course
GET/courses/{id}AllCourse detail
PATCH/courses/{id}⚙️Update course
POST/courses/{id}/publish⚙️Publish
POST/courses/{id}/unpublish⚙️Unpublish
DELETE/courses/{id}Delete (Owner only, with confirmation
header)
POST/courses/{id}/assign-
teacher
⚙️Assign teacher
Example: POST /courses
## // Request
## {
"title": { "en": "Tajweed Fundamentals", "ar": "...", "ur": "..." },
## "description": { "en": "...", "ar": "...", "ur": "..." },
## "course_type": "recorded",
## "teacher_id": "019012...",
"price": { "amount": 150.00, "currency": "USD" },
"thumbnail_url": null
## }
## // Response 201
## { "id": "019013...", "slug": "tajweed-fundamentals", "status": "draft", ... }
## 4.2 Modules
MethodEndpointPermDescription
GET/courses/{course_id}/
modules
AllList modules (students only see unlocked ones
by default)
POST/courses/{course_id}/
modules
⚙️Create module
GET/modules/{id}AllModule detail (enforces unlock state for
students)
PATCH/modules/{id}⚙️Update
DELETE/modules/{id}⚙️Delete
REST API Design SpecificationAl-Uloom Academy Portal
Page 6 of 15

MethodEndpointPermDescription
POST/modules/reorder⚙️Reorder ({course_id, ordered_ids:
## [...]})
## 4.3 Module Content
MethodEndpointPermDescription
POST/modules/{id}/content⚙️Upload content (multipart) — video/audio/pdf/
image
DELETE/content/{id}⚙️Delete content item
GET/content/{id}/signed-
url
## ‍⚙️
## 
Generate short-lived signed URL for download/
stream
- MCQ Quizzes & Attempts
5.1 Quiz Management (Admin)
MethodEndpointPermDescription
GET/modules/{id}/quiz⚙️Full quiz with correct answers (for editing)
PUT/modules/{id}/quiz⚙️Upsert quiz with questions + options
PATCH/quizzes/{id}⚙️Update metadata (time_limit, pass_threshold)
## 5.2 Student Quiz Flow
MethodEndpointPermDescription
GET/modules/{id}/quiz/
start
Fetch questions (answers hidden, shuffled order) —
starts attempt session
POST/quizzes/{id}/attemptSubmit answers; returns score + pass/fail
GET/me/attempts?
module_id={id}
My attempt history for a module
Example: POST /quizzes/{id}/attempt
REST API Design SpecificationAl-Uloom Academy Portal
Page 7 of 15

## // Request
## {
## "answers": [
## { "question_id": "q1", "selected_option_id": "o3" },
## { "question_id": "q2", "selected_option_id": "o1" }
## ]
## }
## // Response 200
## {
## "attempt_id": "019014...",
## "score_pct": 60.0,
"passed": true,
## "pass_threshold": 40,
## "next_module_unlocked": "019015...",
## "correct_count": 6,
## "total": 10
## }
## 6. Live Sessions
## 6.1 Session Management
MethodEndpointPermDescription
GET/live-sessions⚙️List all sessions (filters: course, date, status)
POST/live-sessions⚙️Schedule session
GET/live-sessions/{id}AllSession detail
PATCH/live-sessions/{id}⚙️Reschedule
DELETE/live-sessions/{id}Delete (Owner only)
Example: POST /live-sessions
## {
## "course_id": "019013...",
"scheduled_start": "2026-05-20T16:00:00Z",
## "duration_minutes": 60,
"title": "Week 3 — Tajweed Rules of Noon Sakinah"
## }
REST API Design SpecificationAl-Uloom Academy Portal
Page 8 of 15

## 6.2 Session Runtime
MethodEndpointPermDescription
POST/live-sessions/{id}/
start
‍⚙️Teacher starts session; returns LiveKit URL +
publisher token; triggers egress
POST/live-sessions/{id}/
join
## ‍⚙️
## 
Join session; returns LiveKit URL + token scoped
to role
POST/live-sessions/{id}/
end
‍⚙️End session; stops egress
GET/live-sessions/{id}/
attendance
‍⚙️Attendance roster
Example: POST /live-sessions/{id}/start
## // Response 200
## {
## "livekit_url": "wss://live.aluloom.academy",
## "room_name": "session_019016",
"token": "eyJhbGciOi...",
## "recording_status": "starting"
## }
6.3 LiveKit Webhooks (ingress)
MethodEndpointPermDescription
POST/webhooks/
livekit
## 
## (signed)
Receives egress_started, egress_ended,
room_finished events
## 7. Recordings & Access Control
MethodEndpointPermDescription
GET/recordings⚙️List all recordings (filters)
GET/recordings/{id}Per
access
Recording detail
GET/recordings/{id}/signed-
url
## Per
access
Signed stream URL (1 hour TTL)
REST API Design SpecificationAl-Uloom Academy Portal
Page 9 of 15

MethodEndpointPermDescription
DELETE/recordings/{id}⚙️Delete recording + storage object
POST/recordings/{id}/access⚙️Grant access to user(s): { user_ids:
## [...] }
DELETE/recordings/{id}/access/
## {user_id}
⚙️Revoke access
GET/recordings/{id}/access⚙️List who has access
GET/me/recordings‍Recordings I have access to
## 8. Certificates
MethodEndpointPermDescription
GET/certificates⚙️List all
GET/certificates/{id}Per
access
Certificate detail
GET/certificates/{id}/
download
## Per
access
Signed PDF URL
POST/certificates/{id}/
revoke
⚙️Revoke
POST/certificates/{id}/
reissue
⚙️Regenerate PDF
GET/verify/{cert_id}Public verification endpoint (JSON + HTML
rendering)
Example: GET /verify/{cert_id}
## // Response 200
## {
"cert_id": "ALU-2026-00124",
## "status": "valid",
"student_name": "Aisha Khan",
"course_title": "Tajweed Fundamentals",
"issued_at": "2026-06-10T09:00:00Z",
## "verification_hash": "sha256:a3f2..."
## }
REST API Design SpecificationAl-Uloom Academy Portal
Page 10 of 15

## 9. Messaging
9.1 Message History (REST)
MethodEndpointPermDescription
GET/courses/{id}/
messages
## Members +
## ⚙️
List messages (paginated, newest first)
POST/courses/{id}/
messages
MembersSend message (also available via WebSocket)
POST/messages/{id}/
attachment
MembersUpload attachment (multipart) — returns URL
to include in message body
PATCH/messages/{id}/flag⚙️Flag message for review
DELETE/messages/{id}/hide⚙️Hide from non-admin view (soft delete)
9.2 Real-time (WebSocket)
URL: wss://api.aluloom.academy/ws/courses/{course_id}/chat?
token={access_token}
## Events:
## Client → Server: { "type": "message", "body": "...", "attachments": [...] }
## Server → Client: { "type": "message.new", "message": {...} }, { "type":
## "presence.update", "users": [...] }
## 9.3 Admin Moderation
MethodEndpointPermDescription
GET/admin/messages/search⚙️Full-text search across all messages (filters:
course, user, date, flagged)
GET/admin/conversations⚙️List all course conversations with last-
message preview
GET/admin/conversations/
## {course_id}/export
⚙️Export as CSV/JSON
## •
## •
## •
## •
REST API Design SpecificationAl-Uloom Academy Portal
Page 11 of 15

- Shared Content (Homework / Assignments)
MethodEndpointPermDescription
GET/courses/{id}/shared-contentMembers + ⚙️
## 
List shared items
POST/courses/{id}/shared-content‍Upload shared item
## (multipart)
GET/shared-content/{id}/signed-
url
## Members + ⚙️
## 
Download URL
DELETE/shared-content/{id}Uploader + ⚙️
## 
## Delete
## 11. Enrollment & Payments
## 11.1 Enrollment
MethodEndpointPermDescription
GET/enrollments⚙️List (filters: course, student, status)
POST/enrollments⚙️Manual enrollment (status=ACTIVE)
GET/enrollments/{id}⚙️Detail
POST/enrollments/{id}/revoke⚙️Revoke (status=REVOKED)
GET/enrollments/{id}/progress⚙️(own)Module-by-module progress
## 11.2 Payment Links
MethodEndpointPermDescription
POST/payment-links⚙️Create payment link for (student_id, course_id)
GET/payment-links/{id}⚙️Get status
POST/webhooks/stripe (signed)Stripe webhook
POST/webhooks/razorpay (signed)Razorpay webhook
Example: POST /payment-links
REST API Design SpecificationAl-Uloom Academy Portal
Page 12 of 15

## // Request
## {
## "student_id": "019018...",
## "course_id": "019013...",
"currency": "USD"
## }
## // Response 201
## {
## "id": "019019...",
## "checkout_url": "https://checkout.stripe.com/c/pay/cs_...",
## "enrollment_id": "01901a...",
"expires_at": "2026-05-21T16:00:00Z"
## }
## 11.3 Payments
MethodEndpointPermDescription
GET/payments⚙️List payments (filters)
GET/payments/{id}⚙️Detail
POST/payments/{id}/refundInitiate refund (Owner only)
## 12. Email Campaigns
Listmonk runs at https://mail.aluloom.academy with its own API. Our Django API proxies the
key operations used by the admin UI:
MethodEndpointPermDescription
GET/email-campaigns⚙️List campaigns
POST/email-campaigns⚙️Create (proxies to Listmonk)
POST/email-campaigns/{id}/start⚙️Send now
POST/email-campaigns/{id}/schedule⚙️Schedule
POST/email-campaigns/{id}/pause⚙️Pause
GET/email-campaigns/{id}/stats⚙️Delivery stats
GET/mail-lists⚙️List audience segments
POST/mail-lists/sync⚙️Sync users → Listmonk subscribers
REST API Design SpecificationAl-Uloom Academy Portal
Page 13 of 15

## 13. Dashboard & Analytics
MethodEndpointPermDescription
GET/dashboard/
overview
⚙️Metric cards (students, courses, sessions today, revenue
## MTD)
GET/dashboard/
activity
⚙️Recent activity feed (paginated)
GET/dashboard/storage⚙️MinIO bucket usage
GET/audit-logs⚙️Audit trail (filters: actor, action, entity, date)
## 14. File Upload Strategy
For files > 5 MB, we use pre-signed URL direct-to-MinIO uploads to avoid proxying large files
through Django:
MethodEndpointPermDescription
POST/uploads/
presigned
## All (with
quota)
Returns { upload_url, storage_key, fields,
expires_at }
POST/uploads/
confirm
AllAfter direct upload, caller confirms: { storage_key,
content_type, size } — server verifies and records
Small files (≤ 5 MB) still accept direct multipart on content endpoints for simplicity.
## 15. Rate Limiting
Endpoint classLimit
/auth/login, /auth/forgot-password5 / 15 min / IP
Write endpoints (POST/PATCH/DELETE)60 / min / user
Read endpoints300 / min / user
File uploads10 / min / user
Webhooksunlimited (origin allowlist + signature verification)
REST API Design SpecificationAl-Uloom Academy Portal
Page 14 of 15

- API Versioning
Path-based versioning: /api/v1/...
Breaking changes increment the major version; two versions run side-by-side for min. 6 months
Deprecated endpoints return Deprecation: true and Sunset: <date> headers
- OpenAPI / Developer Experience
Auto-generated OpenAPI 3.1 spec via drf-spectacular
Swagger UI at /api/docs/ (admin-only access in production)
Postman collection generated and checked into repo
Example requests/responses for every endpoint
End of API Design Document
## •
## •
## •
## •
## •
## •
## •
REST API Design SpecificationAl-Uloom Academy Portal
Page 15 of 15