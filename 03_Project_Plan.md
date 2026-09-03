

## AL-ULOOM ACADEMY
## Project Plan
Al-Uloom Online Islamic Academy Management Portal
## Version: 1.0
## Date: April 2026
Status: Draft for Approval
Page 1 of 10

## 1. Executive Summary
We will deliver an MVP of the Academy Management Portal in 12 weeks (~3 months) using a
FOSS-preferred stack (Django + Next.js + LiveKit + PostgreSQL + MinIO + Listmonk). The system
supports live and recorded courses, four user roles, automated MCQ-gated progression, auto-
generated certificates, moderated messaging, and bulk email — all self-hosted on VPS infrastructure
the academy controls.
After MVP launch, Phase 2 (weeks 13–20) adds mobile refinements, advanced analytics, TOTP 2FA,
and a parent portal.
## 2. Approach & Methodology
Agile / 2-week sprints with Friday demo + weekly stakeholder review on Mondays
Vertical slice delivery: each sprint ships something end-to-end usable, not just backend-only
or frontend-only
Trunk-based development with short-lived feature branches + GitHub Actions CI
Staging environment mirrors production; every merge to main auto-deploys to staging
Weekly demo on staging — Owner signs off on each feature before it's considered "done"
- Phase Breakdown (MVP — 12 Weeks)
Phase 0 — Setup (Weeks 1–2)
Requirements finalization + SRS sign-off
Visual design system + component library (trilingual RTL-aware)
VPS provisioning (Hetzner: 1× app node + 1× media node + 1× DB node recommended for
MVP; can consolidate if budget-constrained)
Domain, DNS, SSL setup
CI/CD pipeline (GitHub Actions → SSH → Docker Compose)
Development, staging, production environments
Backup strategy implemented day 1
Deliverables: signed SRS, clickable Figma prototype, running empty environments, CI/CD pipeline
Phase 1 — Foundations (Weeks 2–4)
Django project + PostgreSQL + Redis + DRF scaffold
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
Project PlanAl-Uloom Academy Portal
Page 2 of 10

Authentication: JWT + refresh tokens + forgot password flow
RBAC implementation with 4 roles (Owner/Admin/Teacher/Student)
User CRUD + CSV bulk import
Next.js PWA scaffold: routing, auth UI, trilingual i18n (next-intl), RTL handling, design tokens
MinIO deployment + presigned upload flow
Audit logging middleware
Deliverables: working login/signup, user management screens, PWA installable, RTL validated
Phase 2 — Recorded Courses LMS (Weeks 4–6)
Course & module CRUD (Admin UI)
Content upload pipeline (video via HLS, PDFs, audio, images)
MCQ quiz builder (Admin UI)
Student learning flow: watch/read → attempt quiz → progressive unlock
Pass threshold (40% default, configurable) + enrollment progress tracking
Certificate generation (WeasyPrint + QR + verification hash + public verify page)
Deliverables: end-to-end recorded course flow working: admin builds → student completes →
certificate issued
Phase 3 — Live Classes (Weeks 5–8, parallel to Phase 2)
LiveKit server self-hosted on media node
Session scheduling + JWT token issuance from Django
Teacher "Start Session" flow (including start-off-schedule support)
Student join flow with attendance tracking
LiveKit Egress auto-recording → MinIO
Recording webhook handler + Recording records
Recording access control UI (grant/revoke)
Basic in-session UI (video grid, mute/unmute, leave, chat sidebar)
Deliverables: 1-hour live session with 10+ students, auto-recorded, access-controlled
Phase 4 — Messaging & Email (Weeks 8–10)
Django Channels WebSocket for course chat
Course chat UI with typing indicators, read receipts
File attachments in messages (reuse upload pipeline)
Admin moderation inbox: search, filter, flag, hide, export
Shared content uploads (homework/assignments)
Listmonk deployment + SES relay configuration
Email campaign UI in admin (proxies to Listmonk)
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
## •
## •
## •
## •
## •
Project PlanAl-Uloom Academy Portal
Page 3 of 10

Transactional email templates (welcome, reset, certificate, enrollment)
Deliverables: moderated chat working, first bulk email campaign sent successfully
Phase 5 — Payments & Polish (Weeks 10–11)
Hybrid enrollment (manual + payment link)
Stripe (and/or Razorpay) integration with signed webhook handling
Payment admin dashboard
Dashboard analytics cards (students, revenue MTD, storage, recent activity)
RTL polish and trilingual content QA with native speakers
PWA offline support for already-downloaded recorded content
Deliverables: first real end-to-end paid enrollment, polished trilingual UI
Phase 6 — QA, Hardening & Launch (Weeks 11–12)
Full UAT across all 4 roles (Owner, Admin, Teacher, Student)
Load testing: 30 concurrent live sessions + 500 concurrent users sustained 2 hours
Security audit: automated (ZAP, Snyk, Bandit) + manual code review + light penetration test
Backup + restore drill
Runbooks: daily ops, backup/restore, scaling, incident response
Admin user guide + teacher quick-start + student onboarding doc (trilingual)
Production launch
Deliverables: production-live system, handover complete
## 4. Team Composition
RoleAllocationResponsibility
Tech Lead / Architect100%Architecture, code review, critical-path
features, risk mgmt
## Senior Backend Engineer
(Django)
100%API, auth, data model, LiveKit integration,
Celery jobs
## Senior Frontend Engineer
(Next.js)
100%PWA, UI, i18n/RTL, LiveKit client, real-time
chat
DevOps Engineer50%Infra, CI/CD, monitoring, backups, security
hardening
QA Engineer50% (ramps to 100% in
weeks 10–12)
Test plans, automation, UAT coordination,
bug triage
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
Project PlanAl-Uloom Academy Portal
Page 4 of 10

RoleAllocationResponsibility
UI/UX Designer50% (front-loaded weeks 1–
## 4)
Design system, wireframes, RTL design, user
flows
Project Manager25%Stakeholder comms, sprint ceremonies,
scope mgmt, timeline
Total effort~4.75 FTE × 3 months~57 person-weeks
Arabic/Urdu native-speaker reviewers — engaged ad-hoc in weeks 2, 6, 10 (roughly 8 hours
each).
- Infrastructure & Running Costs (Estimated)
All prices in USD per month. Sized for medium-scale Year 1 (up to 500 students, 30 concurrent
sessions).
5.1 One-Time / Setup
ItemCost
Domain registration (1 year)$15
SSL certificates$0 (Let's Encrypt)
Penetration test (external)$1,500–3,000 one-time
One-time total~$1,500–3,000
## 5.2 Monthly Recurring Infrastructure
ItemSpecMonthly
App server (VPS)Hetzner CCX33: 8 vCPU / 32 GB /
240 GB NVMe
## ~$65
Media server (LiveKit)Hetzner CCX43: 16 vCPU / 64 GB /
## 1 Gbps
## ~$130
Database server (optional separate)Hetzner CCX23: 4 vCPU / 16 GB~$35
Storage (MinIO)Hetzner Storage Box 5 TB or
dedicated storage node
~$12 (5 TB box) or $60
(storage node)
Backup storage (off-site)Hetzner Storage Box 2 TB (off-site
copy)
## ~$8
Project PlanAl-Uloom Academy Portal
Page 5 of 10

ItemSpecMonthly
CloudflareFree tier sufficient for MVP$0
Amazon SES~5k emails/month~$1
Monitoring stack (Prometheus/
Grafana/Loki/GlitchTip)
Self-hosted on app node$0
Monthly subtotal~$250–300
5.3 Variable / Usage-Based
ItemExpected
Payment gateway feesStripe 2.9% + $0.30 per transaction; Razorpay 2% (India). Pass-through —
paid by academy only on real transactions
Bulk email (if exceeding
SES free tier)
SES is $0.10 per 1,000 emails — negligible
BandwidthCloudflare proxies most of it free; LiveKit media bandwidth included in
Hetzner's 20 TB/month (no overages typical)
## 5.4 Annual Running Cost Summary
Minimum (single consolidated VPS, good for ~100 students): ~$2,000/year
Recommended (recommended Year-1 spec above): ~$3,500/year
Headroom / scale-up (if student count doubles): add ~$100/month → ~$4,700/year
Compared to a SaaS equivalent (Zoom + Thinkific + Mailchimp + Stripe) at this scale — which
typically runs $8,000–15,000/year — the FOSS self-hosted approach yields ~60% lower ongoing
costs at the price of requiring DevOps attention (~10 hours/month after launch).
- Development Cost (Indicative Range)
Development cost varies significantly by region and team seniority. To calibrate expectations:
Region profile57 person-weeks at blended rateTotal (USD)
South Asia / MENA mid-level team~$40/hr blended~$91,000
Eastern Europe / Latin America senior team~$70/hr blended~$160,000
Western Europe / North America agency~$130/hr blended~$296,000
Solo full-stack senior (if aggressive scope cut)~$90/hr, ~40 weeks~$144,000
## •
## •
## •
Project PlanAl-Uloom Academy Portal
Page 6 of 10

These are order-of-magnitude figures. The final quote depends on the delivery partner. What's more
useful to fix is the scope (this document) and timeline (12 weeks), and then solicit proposals on that
basis.
- Post-Launch Ongoing Support
Recommended retainer after go-live:
ScopeHours/monthNotes
DevOps & monitoring10Backups, patches, incidents
Bug fixes & small enhancements20Tickets from users/admin
Quarterly security updates5 (avg)Dependency updates, CVE patches
Total~35 hrs/month~$1,500–5,000/month depending on region
## 8. Risks & Mitigations
#RiskLikelihoodImpactMitigation
R1LiveKit self-hosting
operational complexity
(scaling, TURN/STUN
config, network quality)
MediumHighDedicated media node from day 1; load
test in Phase 3; document runbook; have
LiveKit Cloud as contingency fallback (can
switch with minimal code change using
same SDK)
R2Trilingual UI — Arabic/
Urdu RTL edge cases
discovered late
MediumMediumEngage native-speaker reviewers in
weeks 2, 6, 10 (not just at end); design-
system tokens account for RTL from day 1
R3Storage costs spike due
to recordings growing
faster than expected
MediumMediumPer-course retention policies (default 1
year); storage dashboard alerts at 70%
capacity; HLS-transcoded recordings
(~50% smaller than raw MP4)
R4Payment gateway KYC
delays (Stripe/Razorpay
onboarding)
MediumMediumStart KYC in Week 1 parallel to
development; manual enrollment path
works independently of payment
R5Scope creep from Owner
during development
HighHighSRS sign-off at Week 1 is the scope
contract; any change goes through a
formal change request that shifts timeline/
cost
Project PlanAl-Uloom Academy Portal
Page 7 of 10

#RiskLikelihoodImpactMitigation
R6Chat moderation volume
overwhelms admin
## Low (at
MVP scale)
MediumSmart filters + keyword alerts in Phase 2;
admin inbox is search-first, not read-
everything
R7Certificate forgery /
tampering
LowMediumVerification hash + public verify page; QR
code; PDF digital signature in Phase 2
R8Data loss from
infrastructure failure
LowCriticalDaily automated backups + off-site copy +
quarterly restore drill; monitoring alerts on
backup failures
R9DDoS on login or live
sessions
LowHighCloudflare rate limiting + WAF; LiveKit
tokens short-lived
R10Admin/teacher error
deletes valuable content
MediumMediumSoft-delete pattern for courses, sessions,
recordings; Owner-only for hard delete;
audit log of all destructive actions
- Out of Scope for MVP (Phase 2 Backlog)
Deferring these protects the 12-week timeline. They're in the backlog:
Native mobile apps (iOS/Android) — PWA covers mobile for MVP
Advanced analytics / BI dashboards (per-student performance trends, cohort analysis)
Gamification (badges, leaderboards, streaks)
Live class features: breakout rooms, collaborative whiteboard, polls, hand-raise queue
Parent / guardian portal (separate login, child's progress view)
TOTP 2FA for Admin/Owner (MVP uses email-based OTP for reset only)
Automated transcription & captions for recordings
Forum / discussion boards per course
In-app push notifications
Multi-tenant (multiple academies on single instance)
Translation workflow tools (pro translator collaboration UI for content)
SAML / SSO for enterprise customers
- Success Metrics (KPIs post-launch)
MetricTarget (3 months post-launch)
## Uptime≥ 99.5%
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
Project PlanAl-Uloom Academy Portal
Page 8 of 10

MetricTarget (3 months post-launch)
Mean session join latency< 3 seconds
Student course-completion rateEstablish baseline, then target +10% QoQ
Admin moderation coverage100% of messages searchable; no reported off-platform poaching
Support tickets / active user / month< 0.1
Certificate verification page visitsTrack for credibility signal
Email deliverability> 98% delivered (SES metrics)
## 11. Deliverables Checklist
At launch, the academy will receive:
✅ Production-deployed system on their own VPS (root access handed over)
✅ Staging environment mirroring production
✅ Complete source code in private repository (GitHub/GitLab) — academy owns it
✅ Auto-generated OpenAPI spec + Postman collection
✅ Admin user guide (trilingual PDF)
✅ Teacher quick-start guide (trilingual)
✅ Student onboarding guide (trilingual)
✅ Ops runbook: deploy, backup/restore, scale, incident response
✅ Architecture documentation + diagrams
✅ 30 days of post-launch hypercare (priority response)
✅ Knowledge-transfer sessions (3 × 2 hours) for academy's IT staff
## 12. Immediate Next Steps
Owner/Admin sign off on this plan + SRS + API design (this week)
Confirm hosting provider (Hetzner recommended) — or open account (1–2 days)
Start payment gateway KYC (Stripe + Razorpay) — can run in parallel, blocker if delayed
Identify Arabic and Urdu native-speaker reviewers (can be from academy itself)
Provide academy logo, colors, seal/signature images for design system + certificates
Kickoff meeting — scheduled for start of Week 1
Assemble team and provision access (GitHub, Figma, staging VPS)
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
## 1.
## 2.
## 3.
## 4.
## 5.
## 6.
## 7.
Project PlanAl-Uloom Academy Portal
Page 9 of 10

End of Project Plan
Project PlanAl-Uloom Academy Portal
Page 10 of 10