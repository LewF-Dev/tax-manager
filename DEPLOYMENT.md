# Deployment Guide

This guide covers deploying Tax Manager to production using the recommended stack.

## Recommended Stack

- **Database + Auth**: Supabase
- **API Hosting**: Render
- **Monitoring**: Sentry
- **Payments**: Stripe

## Prerequisites

1. Supabase account and project
2. Render account
3. Stripe account (live mode)
4. Sentry account (optional but recommended)
5. Domain name (optional, Render provides subdomain)

## Step 1: Supabase Setup

### 1.1 Create Project

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Create new project
3. Note your project URL and anon key

### 1.2 Get JWT Secret

1. Go to Project Settings → API
2. Copy JWT Secret (under "JWT Settings")

### 1.3 Configure Authentication

1. Go to Authentication → Providers
2. Enable Email provider
3. Configure email templates (optional)
4. Set up redirect URLs for your domain

### 1.4 Database Connection

Your database URL format:
```
postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

## Step 2: Stripe Setup

### 2.1 Create Product and Price

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Products → Add Product
3. Create monthly recurring price
4. Note the Price ID (starts with `price_`)

### 2.2 Get API Keys

1. Developers → API Keys
2. Copy Secret Key (starts with `sk_live_`)
3. Copy Publishable Key (starts with `pk_live_`)

### 2.3 Configure Webhook

1. Developers → Webhooks → Add Endpoint
2. Endpoint URL: `https://your-domain.com/api/v1/billing/webhook`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy Webhook Signing Secret (starts with `whsec_`)

### 2.4 Enable Customer Portal

1. Settings → Billing → Customer Portal
2. Configure portal settings
3. Enable subscription management

## Step 3: Render Deployment

### 3.1 Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. New → Web Service
3. Connect your GitHub repository
4. Configure:
   - **Name**: tax-manager-api
   - **Environment**: Python 3
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3.2 Environment Variables

Add these environment variables in Render:

```bash
# Application
APP_NAME=Tax Manager
APP_VERSION=1.0.0
DEBUG=false
SECRET_KEY=<generate-random-secret>

# Database (from Supabase)
DATABASE_URL=postgresql://postgres:...@db....supabase.co:5432/postgres

# Supabase
SUPABASE_URL=https://....supabase.co
SUPABASE_KEY=<your-anon-key>
SUPABASE_JWT_SECRET=<your-jwt-secret>

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# Sentry (optional)
SENTRY_DSN=https://...@sentry.io/...

# CORS
CORS_ORIGINS=https://your-frontend-domain.com,https://your-domain.com
```

### 3.3 Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3.4 Deploy

1. Click "Create Web Service"
2. Wait for deployment to complete
3. Note your service URL (e.g., `https://tax-manager-api.onrender.com`)

## Step 4: Database Migrations

Migrations run automatically on deployment via the start command.

To run manually:
```bash
# SSH into Render service or run locally
alembic upgrade head
```

## Step 5: Sentry Setup (Optional)

### 5.1 Create Project

1. Go to [Sentry Dashboard](https://sentry.io)
2. Create new project (Python/FastAPI)
3. Copy DSN

### 5.2 Add to Environment

Add `SENTRY_DSN` to Render environment variables.

### 5.3 Initialize in Code

Add to `app/main.py`:

```python
import sentry_sdk
from app.core.config import settings

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
    )
```

## Step 6: Verify Deployment

### 6.1 Health Check

```bash
curl https://your-api-domain.com/health
```

Expected response:
```json
{"status": "healthy"}
```

### 6.2 API Documentation

Visit: `https://your-api-domain.com/docs`

### 6.3 Test Stripe Webhook

1. Stripe Dashboard → Webhooks → Your Endpoint
2. Click "Send test webhook"
3. Check Render logs for successful processing

## Step 7: Custom Domain (Optional)

### 7.1 Add Domain in Render

1. Service Settings → Custom Domain
2. Add your domain
3. Note the CNAME target

### 7.2 Configure DNS

Add CNAME record:
```
api.yourdomain.com → your-service.onrender.com
```

### 7.3 Update CORS

Update `CORS_ORIGINS` environment variable with your custom domain.

## Monitoring

### Application Logs

View in Render Dashboard → Logs

### Database Monitoring

View in Supabase Dashboard → Database → Logs

### Error Tracking

View in Sentry Dashboard (if configured)

### Stripe Events

View in Stripe Dashboard → Developers → Events

## Backup Strategy

### Database Backups

Supabase provides automatic daily backups.

To create manual backup:
1. Supabase Dashboard → Database → Backups
2. Click "Create Backup"

### Export User Data

Users can export their own data via:
```
GET /api/v1/export/full
```

## Scaling Considerations

### Database

Supabase Pro plan provides:
- 8GB database
- 100GB bandwidth
- Automatic backups

Upgrade when approaching limits.

### API Service

Render auto-scales based on traffic.

Monitor:
- Response times
- Error rates
- Memory usage

Upgrade plan if needed.

### Rate Limiting

Consider adding rate limiting for production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

## Security Checklist

- [ ] All environment variables set correctly
- [ ] `DEBUG=false` in production
- [ ] Strong `SECRET_KEY` generated
- [ ] HTTPS enabled (automatic on Render)
- [ ] CORS configured with specific origins
- [ ] Stripe webhook signature verification enabled
- [ ] Database connection uses SSL
- [ ] Sentry configured for error tracking
- [ ] Regular security updates scheduled

## Troubleshooting

### Migration Failures

Check Render logs for Alembic errors.

To rollback:
```bash
alembic downgrade -1
```

### Stripe Webhook Failures

1. Check webhook signature secret matches
2. Verify endpoint URL is correct
3. Check Render logs for errors
4. Test with Stripe CLI:
   ```bash
   stripe listen --forward-to https://your-domain.com/api/v1/billing/webhook
   ```

### Database Connection Issues

1. Verify DATABASE_URL is correct
2. Check Supabase project is active
3. Verify IP allowlist (Supabase allows all by default)

### Authentication Issues

1. Verify SUPABASE_JWT_SECRET matches Supabase project
2. Check token expiration settings
3. Verify CORS allows your frontend domain

## Maintenance

### Updating Tax Rulesets

When HMRC announces new rates:

1. Update `app/core/tax_rulesets.py`
2. Add new tax year ruleset
3. Deploy via git push
4. Verify with test calculation

### Database Migrations

For schema changes:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Review migration file
# Edit if needed

# Deploy (runs automatically on Render)
git push
```

### Monitoring Checklist

Weekly:
- [ ] Check error rates in Sentry
- [ ] Review Stripe failed payments
- [ ] Check database size in Supabase

Monthly:
- [ ] Review API response times
- [ ] Check for security updates
- [ ] Verify backup integrity
- [ ] Review user growth vs. plan limits

## Support

For deployment issues:
- Render: [Render Docs](https://render.com/docs)
- Supabase: [Supabase Docs](https://supabase.com/docs)
- Stripe: [Stripe Docs](https://stripe.com/docs)
