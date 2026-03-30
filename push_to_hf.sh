#!/bin/bash
# Push to HuggingFace Space

echo "🚀 Pushing to HuggingFace Space..."
echo "Space URL: https://huggingface.co/spaces/karthikc1125/aws-architecture-failure-detection-system"
echo ""
echo "⚠️  You need to provide your HuggingFace token:"
echo "  1. Go to: https://huggingface.co/settings/tokens"
echo "  2. Create a 'write' access token"
echo "  3. Paste it below:"
echo ""

read -sp "Enter your HuggingFace token: " HF_TOKEN
echo ""

cd "$(dirname "$0")" || exit

# Configure git with token
git config --global credential.helper store
echo "https://:${HF_TOKEN}@huggingface.co" > ~/.git-credentials
chmod 600 ~/.git-credentials

# Push to HF Space
git push -u hf main

echo ""
echo "✅ Push complete!"
echo "Space URL: https://huggingface.co/spaces/karthikc1125/aws-architecture-failure-detection-system"
