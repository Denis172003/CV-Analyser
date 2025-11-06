# Deployment Guide

This guide covers various deployment options for the AI Resume Analyzer application.

## 🚀 Quick Deployment Options

### 1. Streamlit Cloud (Recommended for Demo)

**Pros**: Free, easy setup, automatic deployments
**Cons**: Limited resources, public repositories only

#### Steps:
1. **Fork the repository** to your GitHub account
2. **Visit** [share.streamlit.io](https://share.streamlit.io)
3. **Connect your GitHub** account
4. **Deploy** by selecting your forked repository
5. **Add secrets** in the Streamlit Cloud dashboard:
   ```
   OPENAI_API_KEY = "your_openai_key"
   SUPABASE_URL = "your_supabase_url"
   SUPABASE_KEY = "your_supabase_key"
   ```

### 2. Heroku Deployment

**Pros**: Easy deployment, good for small to medium apps
**Cons**: Paid plans required for production use

#### Prerequisites:
- Heroku account
- Heroku CLI installed

#### Steps:
1. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```

2. **Add buildpacks**:
   ```bash
   heroku buildpacks:add --index 1 heroku/python
   heroku buildpacks:add --index 2 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set OPENAI_API_KEY="your_key"
   heroku config:set SUPABASE_URL="your_url"
   heroku config:set SUPABASE_KEY="your_key"
   ```

4. **Create Procfile**:
   ```bash
   echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
   ```

5. **Deploy**:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### 3. Docker Deployment

**Pros**: Consistent environment, scalable, works anywhere
**Cons**: Requires Docker knowledge

#### Local Docker:
```bash
# Build image
docker build -t ai-resume-analyzer .

# Run container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY="your_key" \
  -e SUPABASE_URL="your_url" \
  -e SUPABASE_KEY="your_key" \
  ai-resume-analyzer
```

#### Docker Compose:
```bash
# Copy environment variables
cp .env.template .env
# Edit .env with your API keys

# Start services
docker-compose up -d

# View logs
docker-compose logs -f app
```

## ☁️ Cloud Platform Deployments

### AWS Deployment

#### Option 1: AWS App Runner
1. **Build and push** Docker image to ECR
2. **Create App Runner service** from ECR image
3. **Configure environment variables** in App Runner
4. **Set up custom domain** (optional)

#### Option 2: AWS ECS with Fargate
1. **Create ECS cluster**
2. **Define task definition** with container settings
3. **Create service** with load balancer
4. **Configure auto-scaling** policies

#### Option 3: AWS Lambda (Serverless)
```bash
# Install serverless framework
npm install -g serverless

# Deploy with serverless-wsgi plugin
serverless deploy
```

### Google Cloud Platform

#### Cloud Run Deployment:
```bash
# Build and deploy
gcloud run deploy ai-resume-analyzer \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY="your_key"
```

#### App Engine Deployment:
1. **Create app.yaml**:
   ```yaml
   runtime: python310
   
   env_variables:
     OPENAI_API_KEY: "your_key"
     SUPABASE_URL: "your_url"
     SUPABASE_KEY: "your_key"
   
   automatic_scaling:
     min_instances: 0
     max_instances: 10
   ```

2. **Deploy**:
   ```bash
   gcloud app deploy
   ```

### Microsoft Azure

#### Azure Container Instances:
```bash
az container create \
  --resource-group myResourceGroup \
  --name ai-resume-analyzer \
  --image your-registry/ai-resume-analyzer:latest \
  --dns-name-label ai-resume-analyzer \
  --ports 8501 \
  --environment-variables \
    OPENAI_API_KEY="your_key" \
    SUPABASE_URL="your_url"
```

#### Azure App Service:
1. **Create App Service** in Azure Portal
2. **Configure deployment** from GitHub
3. **Set application settings** with environment variables
4. **Configure custom domain** and SSL

## 🔧 Production Configuration

### Environment Variables

#### Required Variables:
```bash
# AI Services
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Optional Services
NUTRIENT_API_KEY=your_nutrient_api_key
GEMINI_API_KEY=your_google_ai_studio_key
GEMINI_PROJECT_ID=your_google_project_id

# Production Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE=200
CACHE_TTL=3600
```

#### Security Variables:
```bash
# Database (if using custom PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:port/db

# Session Management
SECRET_KEY=your_secret_key_for_sessions

# CORS Settings
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### Performance Optimization

#### Streamlit Configuration:
Create `.streamlit/config.toml`:
```toml
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[runner]
magicEnabled = false
installTracer = false
fixMatplotlib = false
```

#### Caching Strategy:
```python
# Add to app.py for production
import streamlit as st

@st.cache_data(ttl=3600)  # Cache for 1 hour
def cached_analysis(resume_text, job_text):
    return ai_integration.call_gpt_analysis(resume_text, job_text)

@st.cache_resource
def init_database():
    return database.init_supabase()
```

### Monitoring and Logging

#### Application Monitoring:
```python
# Add to your app
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

# Configure Sentry for error tracking
sentry_sdk.init(
    dsn="your_sentry_dsn",
    integrations=[LoggingIntegration()],
    traces_sample_rate=0.1,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

#### Health Checks:
```python
# Add health check endpoint
@st.cache_data
def health_check():
    try:
        # Test database connection
        db = database.init_supabase()
        db.table('cv_analyses').select('id').limit(1).execute()
        
        # Test AI service
        ai_integration.call_gpt_analysis("test", "")
        
        return {"status": "healthy", "timestamp": datetime.now()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## 🔒 Security Considerations

### API Key Management
- **Never commit** API keys to version control
- **Use environment variables** or secret management services
- **Rotate keys regularly** and monitor usage
- **Set up billing alerts** for API services

### Application Security
```python
# Input validation
def validate_file_upload(file):
    if file.size > MAX_UPLOAD_SIZE:
        raise ValueError("File too large")
    
    if file.type not in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        raise ValueError("Invalid file type")
    
    return True

# Rate limiting (using streamlit-authenticator)
def check_rate_limit(user_id):
    # Implement rate limiting logic
    pass
```

### Database Security
- **Use connection pooling** for database connections
- **Implement row-level security** in Supabase
- **Regular backups** and disaster recovery plans
- **Monitor for suspicious activity**

## 📊 Scaling Considerations

### Horizontal Scaling
- **Load balancer** configuration for multiple instances
- **Session state management** with external storage
- **Database connection pooling**
- **CDN** for static assets

### Vertical Scaling
- **Memory optimization** for large file processing
- **CPU optimization** for video generation
- **Storage optimization** for temporary files
- **Network optimization** for API calls

### Auto-scaling Configuration
```yaml
# Kubernetes HPA example
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-resume-analyzer-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-resume-analyzer
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 🚨 Troubleshooting

### Common Deployment Issues

#### Port Binding Issues:
```bash
# Check if port is in use
lsof -i :8501

# Use different port
streamlit run app.py --server.port 8502
```

#### Memory Issues:
```bash
# Monitor memory usage
docker stats

# Increase container memory
docker run -m 2g ai-resume-analyzer
```

#### API Rate Limits:
```python
# Implement exponential backoff
import time
import random

def api_call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

### Performance Issues

#### Slow Video Generation:
- **Use smaller video dimensions** for faster processing
- **Implement video generation queue** for multiple users
- **Cache generated videos** for similar content
- **Use GPU instances** for video processing

#### Database Performance:
- **Add database indexes** for frequently queried columns
- **Implement connection pooling**
- **Use read replicas** for read-heavy workloads
- **Monitor query performance**

## 📈 Monitoring and Analytics

### Application Metrics
```python
# Custom metrics collection
import time
from functools import wraps

def track_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        # Log performance metrics
        logger.info(f"{func.__name__} took {duration:.2f} seconds")
        
        return result
    return wrapper
```

### Business Metrics
- **User engagement**: Track feature usage
- **Conversion rates**: Monitor successful analyses
- **Error rates**: Track and alert on failures
- **Performance**: Response times and throughput

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
The included `.github/workflows/ci.yml` provides:
- **Automated testing** on multiple Python versions
- **Code quality checks** with linting and formatting
- **Security scanning** with bandit and safety
- **Docker image building** and pushing
- **Automated deployment** to staging and production

### Deployment Triggers
- **Push to main**: Deploy to production
- **Push to develop**: Deploy to staging
- **Pull requests**: Run tests and checks
- **Release tags**: Create GitHub releases

## 📞 Support and Maintenance

### Backup Strategy
- **Database backups**: Daily automated backups
- **Code backups**: Version control with GitHub
- **Configuration backups**: Environment variables and secrets
- **Disaster recovery**: Documented recovery procedures

### Update Strategy
- **Rolling updates**: Zero-downtime deployments
- **Feature flags**: Gradual feature rollouts
- **Database migrations**: Versioned schema changes
- **Rollback procedures**: Quick rollback capabilities

### Monitoring Alerts
- **Error rate alerts**: High error rates
- **Performance alerts**: Slow response times
- **Resource alerts**: High CPU/memory usage
- **Business alerts**: Low conversion rates

For additional support, please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file or create an issue on GitHub.