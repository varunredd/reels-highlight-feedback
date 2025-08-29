#!/bin/bash
set -e

echo "=============================="
echo "   🚀 Push to Git Repositories"
echo "=============================="
echo "What did you change?"
echo "1) Code (app.py, requirements, src/)"
echo "2) Data (runs/*.json, feedback, clips)"
echo "3) Both"
read -p "Choose [1-3]: " choice

# Always commit staged changes
git add .
read -p "Commit message: " msg
git commit -m "$msg" || echo "⚠️ Nothing to commit."

case $choice in
  1)
    echo "➡️ Pushing CODE changes..."
    git push origin main
    git push hf main
    ;;
  2)
    echo "➡️ Pushing DATA changes..."
    git push origin main
    git push hf-dataset main
    ;;
  3)
    echo "➡️ Pushing BOTH code + data..."
    git push origin main
    git push hf main
    git push hf-dataset main
    ;;
  *)
    echo "❌ Invalid choice"
    ;;
esac

echo "✅ Done!"
