# Configuration Documentation

This document describes all configuration options for redevops.io, including environment variables, service-specific settings, and deployment configurations.

## Quick Start Configuration

### Minimum Required Environment Variables

```bash
# Create a .env file with these minimum settings:
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=redevops
POSTGRES_USER=redevops
POSTGRES_PASSWORD=your_secure_password

OLLAMA_HOST=http://localhost:11434
```

## Environment Variables

### Core Application Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_ENV` | Application environment (`development`, `staging`, `production`) | `production` | No |
| `LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` | No |
| `SECRET_KEY` | Secret key for session encryption and signing | (generated) | Yes* |

*\*Auto-generated if not provided in production*

### Database Configuration (PostgreSQL)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `POSTGRES_HOST` | PostgreSQL server hostname | `localhost` | Yes |
| `POSTGRES_PORT` | PostgreSQL server port | `5432` | No |
| `POSTGRES_DB` | Database name | `redevops` | Yes |
| `POSTGRES_USER` | Database username | `postgres` | Yes |
| `POSTGRES_PASSWORD` | Database password | (none) | Yes |
| `POSTGRES_SSL_MODE` | SSL mode (`disable`, `require`, `verify-ca`, `verify-full`) | `disable` | No |
| `POSTGRES_POOL_SIZE` | Connection pool size | `10` | No |

### LLM Configuration (Ollama)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OLLAMA_HOST` | Ollama server URL | `http://localhost:11434` | Yes |
| `LLM_MODEL` | Model name to use for inference | `llama2` | No |
| `LLM_TEMPERATURE` | Sampling temperature (0.0-1.0) | `0.7` | No |
| `LLM_MAX_TOKENS` | Maximum tokens per response | `4096` | No |
| `LLM_TIMEOUT` | Request timeout in seconds | `300` | No |

### Agent Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AGENT_CHECK_INTERVAL` | Default interval for monitoring checks (minutes) | `60` | No |
| `AGENT_MAX_CONCURRENT` | Maximum concurrent agent executions | `5` | No |
| `AGENT_TIMEOUT` | Agent execution timeout in seconds | `300` | No |
| `HUMAN_APPROVAL_THRESHOLD` | Price change percentage requiring human approval (%) | `10` | No |

### Notification Channels

#### Slack Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL | (none) | No |
| `SLACK_CHANNEL` | Default Slack channel for notifications | `#alerts` | No |

#### Discord Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DISCORD_WEBHOOK_URL` | Discord webhook URL | (none) | No |

#### Email Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `EMAIL_SMTP_HOST` | SMTP server hostname | (none) | Yes* |
| `EMAIL_SMTP_PORT` | SMTP server port | `587` | No |
| `EMAIL_SMTP_USER` | SMTP username | (none) | Yes* |
| `EMAIL_SMTP_PASSWORD` | SMTP password | (none) | Yes* |
| `EMAIL_FROM_ADDRESS` | Sender email address | `alerts@redevops.local` | No |
| `EMAIL_TLS_ENABLED` | Enable TLS for SMTP | `true` | No |

*\*Required if email notifications are enabled*

#### Webhook Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `WEBHOOK_URL` | Generic webhook URL for custom integrations | (none) | No |
| `WEBHOOK_SECRET` | Secret for webhook signature verification | (none) | No |

### Monitoring and Scraping Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SCRAPER_USER_AGENT` | Custom User-Agent header for scrapers | (default) | No |
| `SCRAPER_TIMEOUT` | Request timeout in seconds | `30` | No |
| `SCRAPER_MAX_RETRIES` | Maximum retry attempts | `3` | No |
| `SCRAPER_RATE_LIMIT` | Requests per second per domain | `1` | No |
| `CHANGEDTECTION_INTERVAL` | Default check interval for changedetection.io (minutes) | `60` | No |

### Security Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CORS_ORIGINS` | Comma-separated allowed CORS origins | `*` | No |
| `RATE_LIMIT_REQUESTS` | Requests per minute per IP | `100` | No |
| `SESSION_TIMEOUT` | Session timeout in minutes | `60` | No |

## Service Configuration Files

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: redevops-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-redevops}
      POSTGRES_USER: ${POSTGRES_USER:-redevops}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-change_me}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-redevops}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Ollama LLM Server
  ollama:
    image: ollama/ollama:latest
    container_name: redevops-ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # changedetection.io
  changedetection:
    image: dgtlmoon/changedetection.io:latest
    container_name: redevops-changedetection
    ports:
      - "5000:5000"
    environment:
      BASE_URL: ${CHANGEDTECTION_BASE_URL:-http://localhost:5000}
    volumes:
      - changedetection_data:/data/store

  # redevops API Server
  api:
    build: .
    container_name: redevops-api
    depends_on:
      postgres:
        condition: service_healthy
      ollama:
        condition: service_started
      changedetection:
        condition: service_started
    environment:
      - APP_ENV=${APP_ENV:-production}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_DB=${POSTGRES_DB:-redevops}
      - POSTGRES_USER=${POSTGRES_USER:-redevops}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-change_me}
      - OLLAMA_HOST=http://ollama:11434
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL:-}
      - DISCORD_WEBHOOK_URL=${DISCORD_WEBHOOK_URL:-}
      - EMAIL_SMTP_HOST=${EMAIL_SMTP_HOST:-}
      - EMAIL_SMTP_PORT=${EMAIL_SMTP_PORT:-587}
      - EMAIL_SMTP_USER=${EMAIL_SMTP_USER:-}
      - EMAIL_SMTP_PASSWORD=${EMAIL_SMTP_PASSWORD:-}
    ports:
      - "8000:8000"

volumes:
  postgres_data:
  ollama_data:
  changedetection_data:
```

### Agent Workflow Configuration

```yaml
# agents/config.yaml
version: "1.0"

agents:
  collector:
    max_concurrent: 5
    timeout_seconds: 300
    retry_policy:
      max_retries: 3
      backoff_multiplier: 2
    
  analyzer:
    max_concurrent: 3
    timeout_seconds: 600
    sensitivity: medium
    
  context:
    max_concurrent: 2
    timeout_seconds: 300
    historical_lookback_days: 90
    
  summarizer:
    max_concurrent: 2
    timeout_seconds: 600
    output_format: markdown
    
  dispatcher:
    max_concurrent: 5
    channels:
      - slack
      - email
      - webhook

human_approval:
  enabled: true
  threshold_percentage: 10
  required_for:
    - pricing_changes
    - new_competitors
    - major_feature_launches
```

### Monitoring Configuration (changedetection.io)

```yaml
# monitors/config.yaml
version: "1.0"

default_settings:
  check_interval_minutes: 60
  ignore_text_patterns: []
  extract_title: true
  extract_links: true
  
monitors:
  - name: competitor-pricing
    url: https://competitor-a.com/pricing
    check_interval: 30
    alert_on_change: true
    tags: [pricing, critical]
    
  - name: competitor-features
    url: https://competitor-a.com/features
    check_interval: 60
    alert_on_change: true
    tags: [features]
    
  - name: competitor-blog
    url: https://competitor-a.com/blog
    check_interval: 120
    alert_on_change: false
    tags: [announcements, blog]

scrapers:
  job-board-monitor:
    target_urls:
      - https://competitor-a.com/careers
      - https://competitor-b.com/jobs
    check_interval: 1440  # Daily
    extract_fields:
      - title
      - location
      - posted_date
      
  review-platform-monitor:
    platforms:
      - name: g2
        url_template: "https://g2.com/products/{product}/reviews"
      - name: capterra
        url_template: "https://capterra.com/p/{product-id}/reviews"
    check_interval: 1440
```

## Deployment-Specific Configuration

### Development Environment

```bash
# .env.development
APP_ENV=development
LOG_LEVEL=DEBUG

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=redevops_dev
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

OLLAMA_HOST=http://localhost:11434
LLM_MODEL=llama2

# Disable rate limiting in development
RATE_LIMIT_REQUESTS=999999

# Local notification channels only
SLACK_WEBHOOK_URL=""
DISCORD_WEBHOOK_URL=""
```

### Production Environment

```bash
# .env.production
APP_ENV=production
LOG_LEVEL=INFO

POSTGRES_HOST=db.example.com
POSTGRES_PORT=5432
POSTGRES_DB=redevops_prod
POSTGRES_USER=redevops_prod
POSTGRES_PASSWORD=<secure_password>
POSTGRES_SSL_MODE=require
POSTGRES_POOL_SIZE=20

OLLAMA_HOST=http://ollama.internal:11434
LLM_MODEL=llama2
LLM_TEMPERATURE=0.5
LLM_MAX_TOKENS=2048

# Production notification channels
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx

EMAIL_SMTP_HOST=smtp.example.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=noreply@example.com
EMAIL_SMTP_PASSWORD=<secure_password>
EMAIL_FROM_ADDRESS=redevops@example.com

# Security settings
CORS_ORIGINS=https://app.example.com
RATE_LIMIT_REQUESTS=60
SESSION_TIMEOUT=30
```

## Configuration Validation

Run the configuration validator before deployment:

```bash
# Validate configuration
python -m redevops.config validate

# Check database connectivity
python -m redevops.config check-db

# Test notification channels
python -m redevops.config test-notifications
```

## Environment Variable Precedence

Configuration is loaded in the following order (highest priority first):

1. Command-line arguments
2. Environment variables
3. `.env` file in project root
4. Default values

## Secrets Management

For production deployments, use a secrets manager:

### Docker Secrets

```yaml
# docker-compose.secrets.yml
services:
  api:
    secrets:
      - postgres_password
      - secret_key
      
secrets:
  postgres_password:
    external: true
  secret_key:
    external: true
```

### Kubernetes Secrets

```bash
# Create secrets from file
kubectl create secret generic redevops-secrets \
  --from-file=.env.production
  
# Or from literal values
kubectl create secret generic redevops-db-password \
  --from-literal=password='<secure_password>'
```

## Troubleshooting Configuration Issues

### Common Problems

1. **Database Connection Failed**
   - Verify `POSTGRES_HOST` and `POSTGRES_PORT` are correct
   - Check PostgreSQL is running and accessible
   - Confirm credentials in environment variables

2. **Ollama Not Responding**
   - Ensure Ollama service is running: `ollama serve`
   - Verify `OLLAMA_HOST` points to correct URL
   - Check if model is pulled: `ollama pull llama2`

3. **Notifications Not Sending**
   - Test webhook URLs manually
   - Verify SMTP credentials for email
   - Check firewall rules for outbound connections

4. **Agent Timeouts**
   - Increase `AGENT_TIMEOUT` in environment variables
   - Reduce `AGENT_MAX_CONCURRENT` if system is overloaded
   - Check resource availability (CPU, memory)
