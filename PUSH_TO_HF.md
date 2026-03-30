# Push to HuggingFace Spaces

Your project is ready to deploy to HuggingFace Spaces!

## Steps to Deploy

### 1. Create HF Token
- Go to: https://huggingface.co/settings/tokens
- Click "New token"
- Select "Write" permission
- Copy the token

### 2. Configure Git
```bash
# Add credentials
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

### 3. Push to HF Space
**Option A: Using the script (recommended)**
```bash
bash push_to_hf.sh
# Paste your HF token when prompted
```

**Option B: Manual push**
```bash
# Add HF remote
git remote add hf https://huggingface.co/spaces/karthikc1125/aws-architecture-failure-detection-system

# Configure credentials
git config credential.helper store
echo "https://<YOUR_HF_TOKEN>@huggingface.co" > ~/.git-credentials
chmod 600 ~/.git-credentials

# Push
git push -u hf main
```

## What Happens After Push

1. **GitHub Integration**: GitHub → HF Spaces auto-sync
2. **Docker Build**: HF automatically builds Docker image
3. **Deployment**: App deploys at:
   ```
   https://huggingface.co/spaces/karthikc1125/aws-architecture-failure-detection-system
   ```
4. **Auto-restart**: Restarts on code changes

## What's Included in HF Spaces

- **app_hf.py**: Gradio web interface
- **Dockerfile**: Docker configuration
- **requirements-hf.txt**: Dependencies
- **API backend**: FastAPI service
- **ML models**: Sentence-transformers + FAISS

## Using Your Space

1. Open: https://huggingface.co/spaces/karthikc1125/aws-architecture-failure-detection-system
2. Describe your AWS architecture
3. Click "Analyze"
4. Get failure predictions and recommendations

## Features on HF Spaces

✅ **Web Interface**: No installation needed
✅ **Real-time Analysis**: Instant results
✅ **Public Access**: Share with anyone
✅ **Auto-scaling**: HF handles load
✅ **Environment Variables**: Set secrets via HF UI
✅ **Persistent Storage**: Store analysis history

## Troubleshooting

### Build fails
- Check `requirements-hf.txt` dependencies
- Reduce dependencies if disk space is an issue
- Use `requirements.txt` (which is smaller)

### Space won't start
- Check logs in HF Space settings
- Verify `app_hf.py` is correct
- Check that port 7860 is used

### Slow response
- HF Spaces free tier has CPU limits
- Upgrade to GPU if needed
- Use simulation mode instead of API calls

## Next Steps

1. **Push code**: Run `bash push_to_hf.sh`
2. **Wait for build**: Takes 2-5 minutes
3. **Test space**: Click link and try it
4. **Share**: Send link to others
5. **Monitor**: Check HF dashboard for usage

---

**Space URL**: https://huggingface.co/spaces/karthikc1125/aws-architecture-failure-detection-system
**GitHub Repo**: https://github.com/karthikc1125/aws-architecture-failure-detection-system
