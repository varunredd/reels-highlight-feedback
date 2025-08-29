#!/bin/bash
set -e

CLEAN_ALL=${1:-false}

if [ "$CLEAN_ALL" = true ]; then
  echo "🧹 Cleaning EVERYTHING (clips, audio, transcripts, runs, reviews, datasets, models)"
  rm -rf data/audio/* data/clips/* data/transcripts/* runs/* notebooks/reviews/* data/datasets/* models/highlight-text-regressor/*
else
  echo "🧹 Cleaning working dirs (clips, audio, transcripts)"
  rm -rf data/audio/* data/clips/* data/transcripts/*
fi

echo "🎬 Running pipeline..."
python -m src.pipeline

echo "🌐 Launching feedback UI..."
python notebooks/gradio_feedback_demo.py

echo "📦 Consolidating feedback..."
python -m src.ml.build_feedback_dataset

echo "🧠 Retraining transformer model..."
python -m src.ml.train_text_regressor

echo "✅ Full cycle completed!"
