#!/bin/zsh

if ! pgrep -f "ollama serve" > /dev/null; then
    echo "Starting ollama server..."
    ollama serve > /dev/null 2>&1 &
else
    echo "ollama is already running"
fi

cd ~/coding\ shenanigans/projects/dumbva
source ~/coding\ shenanigans/projects/dumbva/.venv/bin/activate
python src/main.py