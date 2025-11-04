# Demo-Stable Branch Protection Guidelines

## 🚫 NEVER MODIFY demo-stable branch directly

The `demo-stable` branch contains a frozen snapshot of the working demo environment.
This branch should NEVER be modified after initial creation.

## ✅ Only Allowable Operations:
- Read/clone the branch
- Create new branches FROM demo-stable
- Tag releases from demo-stable
- Deploy from demo-stable

## ❌ Forbidden Operations:
- Direct commits to demo-stable
- Direct pushes to demo-stable
- Force pushes to demo-stable
- Merging into demo-stable
- Rebasing demo-stable

## 🔄 Development Workflow:
1. Create feature branches from `main`
2. Develop and test on feature branches
3. Merge to `main` when ready
4. Create new demo versions by branching from `main` to `demo-stable-v2`, etc.

## 🏷️ Versioning:
- demo-stable = Current demo (frozen)
- demo-stable-v2 = Next demo version (when needed)
- main = Active development

## ⚠️ Emergency Changes:
If critical demo fixes are needed:
1. Create feature branch from demo-stable
2. Make minimal fix
3. Test thoroughly
4. Get approval from all stakeholders
5. Merge to main first
6. Then cherry-pick to demo-stable (with force if necessary)

## 📞 Contact:
Before making ANY changes to demo-stable, contact the development team lead.

