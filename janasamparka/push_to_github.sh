#!/bin/bash
# Push to GitHub - Run this after creating a repository on GitHub

echo "🚀 Push to GitHub Guide"
echo "======================="
echo ""
echo "Step 1: Create a new repository on GitHub"
echo "  Go to: https://github.com/new"
echo "  Name: janasamparka (or your preferred name)"
echo "  Description: MLA Connect - Citizen Complaint Management System"
echo "  Do NOT initialize with README (we already have one)"
echo ""
echo "Step 2: Copy the repository URL (it will look like):"
echo "  https://github.com/YOUR-USERNAME/janasamparka.git"
echo ""
read -p "Enter your GitHub repository URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ No URL provided. Exiting."
    exit 1
fi

echo ""
echo "Setting up remote..."
git remote add origin "$REPO_URL"

echo ""
echo "Pushing main branch..."
git push -u origin main

echo ""
echo "Pushing demo-stable branch..."
git push origin demo-stable

echo ""
echo "Pushing tags..."
git push origin v1.0.0-demo

echo ""
echo "✅ Successfully pushed to GitHub!"
echo ""
echo "📋 Your repository now has:"
echo "  ✅ main branch (production development)"
echo "  ✅ demo-stable branch (frozen demo state)"
echo "  ✅ v1.0.0-demo tag (snapshot)"
echo ""
echo "🌐 View your repository at:"
echo "  $REPO_URL"
echo ""
echo "🚀 To clone elsewhere:"
echo "  git clone $REPO_URL"
echo "  cd janasamparka"
echo "  git checkout demo-stable  # For demo"
echo "  git checkout main         # For production"
