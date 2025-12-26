#!/bin/bash
# Post-deployment script for Render
# This runs after the build completes

echo "🚀 Running post-deployment setup..."

# Run auto-ingestion if needed
echo "📦 Checking if data ingestion is needed..."
poetry run python -m app.scripts.auto_ingest || echo "⚠️ Auto-ingestion skipped or failed"

echo "✅ Post-deployment setup complete"
