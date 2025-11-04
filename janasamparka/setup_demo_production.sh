#!/bin/bash
# Setup Demo and Production Git Structure
# Run: bash setup_demo_production.sh

set -e

echo "🚀 Setting up Demo and Production Git Structure"
echo "================================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Commit current state
echo -e "\n${BLUE}Step 1: Committing current demo state...${NC}"
git add backend/seed_database.py
git add backend/create_department_users.py
git add backend/create_moderator.py
git add backend/delete_dept_officers.py
git add SEEDING_GUIDE.md
git add GIT_COMMIT_CHECKLIST.md
git add DEMO_DEPLOYMENT_GUIDE.md
git add admin-dashboard/src/pages/Login.jsx

git commit -m "feat: Complete stable demo environment

- Database seeding with 21 test users (3 moderators, 15 dept officers, 3 auditors)
- All phone numbers in correct Indian format (+91 followed by 10 digits)
- 16 sample complaints in Puttur on actual roads
- Login page with quick-access test user buttons
- Comprehensive documentation for state restoration
- Map fixes with correct coordinate center

This commit represents a stable, deployable demo state.

Test Credentials:
- Moderators: +919900000000-02 / demo
- Dept Officers: +9199001000-5200 / demo
- Auditors: +9199006000-02 / demo

Can be deployed anywhere with: 
  git checkout demo-stable
  docker compose up -d
  docker compose exec backend python seed_database.py"

echo -e "${GREEN}✅ Committed demo state${NC}"

# 2. Create demo branch
echo -e "\n${BLUE}Step 2: Creating demo-stable branch...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
git checkout -b demo-stable 2>/dev/null || git checkout demo-stable
echo -e "${GREEN}✅ Created/switched to demo-stable branch${NC}"

# 3. Tag the demo version
echo -e "\n${BLUE}Step 3: Tagging demo version...${NC}"
git tag -a v1.0.0-demo -m "Stable Demo Environment v1.0.0

Complete demo setup with:
- 3 Moderators (+919900000000, +919900000001, +919900000002)
- 15 Department Officers (+9199001000 to +9199005200)
- 3 Auditors (+9199006000, +9199006001, +9199006002)
- 16 Sample complaints in Puttur
- All features working
- Ready for deployment

Deploy with:
  git checkout tags/v1.0.0-demo
  docker compose up -d
  docker compose exec backend python seed_database.py

Login: Any test phone number / password: demo"

echo -e "${GREEN}✅ Tagged as v1.0.0-demo${NC}"

# 4. Push everything
echo -e "\n${BLUE}Step 4: Pushing to remote...${NC}"
echo -e "${YELLOW}This will push demo-stable branch and v1.0.0-demo tag${NC}"
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin demo-stable
    git push origin v1.0.0-demo
    echo -e "${GREEN}✅ Pushed demo branch and tag to remote${NC}"
else
    echo -e "${YELLOW}⚠️  Skipped push. Run manually:${NC}"
    echo "  git push origin demo-stable"
    echo "  git push origin v1.0.0-demo"
fi

# 5. Switch back to main
echo -e "\n${BLUE}Step 5: Switching back to main branch...${NC}"
git checkout "$CURRENT_BRANCH"
echo -e "${GREEN}✅ Switched back to $CURRENT_BRANCH${NC}"

# Summary
echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}🎉 Demo and Production Setup Complete!${NC}"
echo -e "${GREEN}================================================${NC}"

echo -e "\n${BLUE}📋 What was created:${NC}"
echo "  ✅ demo-stable branch - Frozen demo state"
echo "  ✅ v1.0.0-demo tag - Specific version snapshot"
echo "  ✅ Back on $CURRENT_BRANCH - Continue production work"

echo -e "\n${BLUE}🚀 Deploy Demo Anywhere:${NC}"
echo "  git clone <your-repo-url> demo-deployment"
echo "  cd demo-deployment"
echo "  git checkout demo-stable"
echo "  cd janasamparka"
echo "  docker compose up -d"
echo "  docker compose exec backend python seed_database.py"

echo -e "\n${BLUE}💻 Continue Production Work:${NC}"
echo "  git checkout main"
echo "  # Make changes"
echo "  git add ."
echo "  git commit -m 'production changes'"
echo "  git push origin main"

echo -e "\n${BLUE}📖 See DEMO_DEPLOYMENT_GUIDE.md for full details${NC}"
