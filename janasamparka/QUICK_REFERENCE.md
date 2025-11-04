# 🚀 Quick Reference: Demo vs Production

## One-Time Setup

```bash
# Run this once to set everything up
bash setup_demo_production.sh
```

This creates:
- ✅ `demo-stable` branch (frozen demo state)
- ✅ `v1.0.0-demo` tag (snapshot)
- ✅ Keeps `main` for production work

---

## Deploy Demo (Anytime, Anywhere)

```bash
git clone <repo-url> demo-deployment
cd demo-deployment
git checkout demo-stable
cd janasamparka
docker compose up -d
sleep 60
docker compose exec backend python seed_database.py
```

**Access**: http://localhost:3000/login
**Login**: `+9199001000` / `demo`

---

## Deploy Production

```bash
git clone <repo-url> production
cd production
git checkout main
cd janasamparka
docker compose -f docker-compose.production.yml up -d
# No seeding - uses real data
```

---

## Development Workflow

### Demo Branch (Frozen)
```bash
git checkout demo-stable
# Only make critical bug fixes
git commit -m "fix: critical demo bug"
git push origin demo-stable
```

### Production Branch (Active)
```bash
git checkout main
# Regular development
git add .
git commit -m "feat: new feature"
git push origin main
```

---

## Quick Commands

| Task | Command |
|------|---------|
| **Switch to Demo** | `git checkout demo-stable` |
| **Switch to Production** | `git checkout main` |
| **Deploy Demo** | `git checkout demo-stable && docker compose up -d` |
| **Deploy Production** | `git checkout main && docker compose -f docker-compose.production.yml up -d` |
| **Reset Demo Data** | `docker compose down -v && docker compose up -d && docker compose exec backend python seed_database.py` |
| **Update Demo** | `git checkout demo-stable && git pull && docker compose up -d --build` |
| **Update Production** | `git checkout main && git pull && docker compose up -d --build` |

---

## Demo Test Users

**Moderators**: `+919900000000`, `+919900000001`, `+919900000002`
**Dept Officers**: `+9199001000` to `+9199005200` (15 total)
**Auditors**: `+9199006000`, `+9199006001`, `+9199006002`
**Password**: `demo` (all users)

---

## Directory Structure Recommendation

```
/home/youruser/
├── janasamparka-demo/          # Demo deployment (demo-stable)
│   └── janasamparka/
│       ├── docker-compose.yml
│       └── ...
│
├── janasamparka-production/    # Production deployment (main)
│   └── janasamparka/
│       ├── docker-compose.production.yml
│       └── ...
│
└── janasamparka-dev/           # Your development work (main)
    └── janasamparka/
        └── ...
```

---

## Branches

| Branch | Purpose | Changes | Data |
|--------|---------|---------|------|
| **demo-stable** | Demos, training | ❌ Frozen | Test users |
| **main** | Production | ✅ Active dev | Real users |

---

## Emergency Reset Demo

```bash
# Nuclear option - fresh start
cd janasamparka-demo/janasamparka
docker compose down -v
docker compose up -d
sleep 60
docker compose exec backend python seed_database.py
```

Demo is now fresh again with all 21 test users! ✨

---

## See Full Documentation

- `DEMO_DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `SEEDING_GUIDE.md` - Database seeding details
- `GIT_COMMIT_CHECKLIST.md` - Git workflow checklist
