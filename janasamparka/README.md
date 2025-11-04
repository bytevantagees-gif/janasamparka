# 🏛️ Janasamparka (ಜನಸಂಪರ್ಕ) - MLA Connect App

**Bilingual Smart Constituency Governance Platform**

Connecting citizens, MLAs, and government departments for faster grievance resolution, data-driven governance, and transparent rural development.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ with PostGIS (or use Docker)
- Git

### Setup (Local Development)

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd janasamparka
```

#### 2. Start with Docker Compose (Recommended)

```bash
# Start all services (database + backend)
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Access API docs
open http://localhost:8000/docs
```

The API will be available at `http://localhost:8000`

#### 3. Manual Setup (Without Docker)

**Backend Setup:**

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and update DATABASE_URL if needed

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Database Setup (if not using Docker):**

```bash
# Install PostgreSQL with PostGIS
# On macOS:
brew install postgresql postgis

# Create database
createdb janasamparka_db

# Enable PostGIS extension
psql janasamparka_db -c "CREATE EXTENSION postgis;"
```

---

## 📖 API Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🧪 Testing the API

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Request OTP

```bash
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'
```

Response (in development mode):
```json
{
  "message": "OTP sent successfully",
  "phone": "+919876543210",
  "otp": "123456",
  "expires_in_minutes": 5
}
```

### 3. Verify OTP & Get Token

```bash
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543210",
    "otp": "123456"
  }'
```

### 4. Create a Complaint

```bash
curl -X POST http://localhost:8000/api/complaints/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Pothole on Main Road",
    "description": "Large pothole near bus stand causing accidents",
    "category": "road",
    "lat": 12.9141,
    "lng": 75.2479,
    "location_description": "Near Bus Stand, Main Road"
  }'
```

### 5. List Complaints

```bash
curl http://localhost:8000/api/complaints/
```

### 6. Get Statistics

```bash
curl http://localhost:8000/api/complaints/stats/summary
```

---

## 📁 Project Structure

```
janasamparka/
├── backend/
│   ├── app/
│   │   ├── core/           # Core config, database, security
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routers/        # API route handlers
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic (future)
│   │   ├── tests/          # Unit and integration tests
│   │   └── main.py         # FastAPI application
│   ├── alembic/            # Database migrations
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/               # Flutter mobile app (coming soon)
├── admin-dashboard/        # React admin panel (coming soon)
├── infra/                  # Infrastructure code
├── docs/                   # Documentation
├── docker-compose.yml
└── README.md
```

---

## 🗄️ Database Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View migration history
alembic history
```

---

## 🛠️ Development

### Code Quality

```bash
# Format code with Black
black app/

# Lint with flake8
flake8 app/

# Type checking with mypy
mypy app/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_auth.py
```

---

## 🏗️ Current Features (Phase 1 MVP)

- ✅ OTP-based authentication (development mode)
- ✅ User management
- ✅ Complaint CRUD operations
- ✅ Complaint assignment to departments
- ✅ Status tracking with logs
- ✅ Basic analytics/statistics
- ✅ PostgreSQL with PostGIS support
- ✅ Docker Compose setup
- ✅ API documentation (Swagger/ReDoc)

---

## 🔜 Coming Soon

- [ ] JWT authentication middleware
- [ ] File upload (media attachments)
- [ ] Voice-to-text integration (Kannada)
- [ ] Map visualization endpoints
- [ ] Polls & voting system
- [ ] Flutter mobile app
- [ ] React admin dashboard
- [ ] AI duplicate detection
- [ ] Bhoomi API integration
- [ ] Push notifications

---

## 🌍 Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key (change in production!)
- `DEBUG` - Enable debug mode
- `CORS_ORIGINS` - Allowed CORS origins

---

## 📝 API Endpoints

### Authentication
- `POST /api/auth/request-otp` - Request OTP
- `POST /api/auth/verify-otp` - Verify OTP & get tokens
- `GET /api/auth/me` - Get current user

### Users
- `GET /api/users/{user_id}` - Get user by ID
- `PATCH /api/users/{user_id}` - Update user profile

### Complaints
- `POST /api/complaints/` - Create complaint
- `GET /api/complaints/` - List complaints (with filters)
- `GET /api/complaints/{id}` - Get complaint details
- `POST /api/complaints/{id}/assign` - Assign to department
- `PATCH /api/complaints/{id}/status` - Update status
- `GET /api/complaints/stats/summary` - Get statistics

---

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and code quality checks
4. Submit a pull request

---

## 📞 Support

For issues or questions, please create an issue in the repository.

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- ByteVantage Enterprise Solutions
- HPE GreenLake Infrastructure
- Puttur Constituency, Karnataka

**Version:** 1.0.0-alpha  
**Last Updated:** October 2025
