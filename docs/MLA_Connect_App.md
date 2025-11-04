# Janasamparka (ಜನಸಂಪರ್ಕ) – MLA Connect App

**Empowering citizens. Enabling leaders. Enhancing governance.**

## 🧭 Vision
To build a bilingual (Kannada + English) smart constituency ecosystem that connects citizens, MLAs, and government departments for faster grievance resolution, data-driven governance, and transparent rural development.

This app becomes a one-stop citizen companion — providing:
- **Governance** (complaints, MLA connect, schemes)
- **Guidance** (self-help, documents, how-to guides)
- **Growth** (jobs, agriculture, training, welfare tracking)

## 🌟 Stakeholder Benefits

| Stakeholder | Key Benefits |
|-------------|-------------|
| **Citizens** | Voice-based grievance system, access to services, awareness of welfare schemes, and participation in decision-making. |
| **MLA & Office** | Real-time view of constituency issues, automatic project tracking, and analytics for better public communication. |
| **Departments** | Simplified case tracking, task completion interface, and geo-proof-based reporting. |
| **Bureaucrats** | Centralized workflow dashboard, AI summaries, faster approvals, and accountability logs. |

## ⚙️ Core Modules & Features

### 🗣️ A. Citizen Services & Grievances
- Complaint System (text, photo, or Kannada voice input)
- AI Duplicate Detection to merge similar complaints automatically
- Geo-Tagged Evidence Uploads
- Complaint Tracking Dashboard
- Public View: citizens see resolved issues in their ward

### 🏛️ B. MLA Interaction & Transparency
- MLA Dashboard with all pending/closed complaints, heatmap by ward
- Map of Works – ongoing and completed projects visualized with pins
- Media Gallery – videos/photos from MLA field visits
- Public Polls – collect citizens' feedback on development priorities
- Jana Mana (ಜನಮನ) – register for people's meeting or video meet
- Weekly MLA Schedule – where the MLA is visiting today/tomorrow

### 🏢 C. Department & Bureaucrat Interface
- Department Logins – Each case can be routed automatically
- Case Resolution Logs – with before/after images and remarks
- Auto Reports – MLA dashboard shows completion rates and delays
- Supervisor Verification – confirm completion before closure

### 🌾 D. Citizen Help & Guidance (Self-Help Zone)
Step-by-step guides (voice + visuals) for:
- Caste/Income/Ration/Pension/Certificates
- Land RTC & Mutation (via Bhoomi API)
- Health Cards, PHC access, Ayushman Bharat
- School admissions, scholarships, hostel applications
- Farmer insurance, crop loans, PM-Kisan, Raita Samparka Kendras

### 🌾 E. Farmer & Livelihood Services
- Daily Market Rates – APMC / e-Raithu integration
- Weather Updates & Crop Advice (KSNDMC integration)
- Fertilizer & Seed Availability Info
- Soil Testing & Irrigation Alerts
- Success Stories Section – share local farming innovations

### 📰 F. Local News & Development Updates
- Verified Constituency News Feed – curated from official sources
- Progress Board – Completed vs ongoing projects
- Government Schemes Section – latest updates & eligibility

### 🗳️ G. Polls, Feedback, and Civic Engagement
- Ward-level Polls – "Which road should be repaired first?"
- Performance Feedback – citizens rate MLA or departments
- Discussion Wall – for community input & verified suggestions
- Volunteer Enrollment – youth can register to help elderly citizens

### 🗺️ H. Map Visualization
- Live pins showing:
  - Active works
  - Citizen complaints
  - MLA visits
  - Panchayat offices & PHCs
- Clicking a pin opens details, photos, and department handling it.
- Citizens can add problem pins (e.g., water leak, pothole).

### 🧠 I. Smart Features
- Kannada AI Voice Chatbot – "Where can I apply for pension?"
- Offline Access Mode – for villages with poor connectivity
- AI Prioritization – highlight urgent issues affecting multiple users
- Automatic Language Translation (Kannada ↔ English)
- Data Analytics Dashboard for MLA and officers

### 🧰 J. Administration & Analytics
- Complaint statistics per ward / category / department
- Officer-level accountability reports
- Performance leaderboard (best-performing departments)
- Automated weekly constituency report PDF for MLA

## 🚀 Implementation Roadmap

### Phase 1 — Foundation (MVP) — 8–12 weeks
**Deliverables:**
- FastAPI backend scaffolding (Auth, Users, Complaints, Departments, Wards)
- PostgreSQL schema + Alembic
- Flutter app skeleton (i18n en + kn, OTP mock, complaint form)
- React admin skeleton (complaints list + assign)

### Phase 2 — Core Features (3–4 months)
- Full complaint lifecycle
- Department workflows
- Basic reporting
- Mobile app core features

### Phase 3 — Engagement & Communication (2 months)
- News feed
- Video Meet integration
- Jana Mana module

### Phase 4 — Rural Empowerment (3 months)
- Farmer services
- Self-help guides
- SHG module

### Phase 5 — Analytics & Expansion (2 months)
- Advanced analytics
- Multi-MLA support
- Performance dashboards

## 🛠️ Tech Stack
- **Frontend**: Flutter (Mobile), ReactJS (Admin Dashboard)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Authentication**: Firebase Auth
- **Storage**: Firebase Storage
- **Maps**: Mapbox/Google Maps API
- **AI/ML**: Python (NLTK, TensorFlow)
- **DevOps**: Docker, GitHub Actions

## 📊 Testing Strategy
- Unit tests (pytest, Jest)
- Integration tests
- E2E tests (Cypress, Flutter Driver)
- Performance testing
- Security testing

## 📝 Local Development Setup

### Backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (Mobile):
```bash
cd mobile
flutter pub get
flutter run
```

### Admin Dashboard:
```bash
cd admin-dashboard
npm install
npm start
```

## 📜 License
MIT License - Feel free to use and contribute!
