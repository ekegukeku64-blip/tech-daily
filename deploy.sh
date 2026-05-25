#!/bin/bash
set -e

echo "Building..."
npm run build

echo "Deploying to GitHub Pages..."
TEMP_DIR=$(mktemp -d)
cp -r dist/* "$TEMP_DIR/"
cd "$TEMP_DIR"
git init -q
git config user.email "deploy@bot"
git config user.name "deploy"
git checkout -b gh-pages -q
git add -A
git commit -m "deploy $(date +%Y-%m-%d_%H:%M)" -q
git remote add origin https://github.com/ekegukeku64-blip/tech-daily.git
git push origin gh-pages --force -q
echo "Done! https://ekegukeku64-blip.github.io/tech-daily/"
