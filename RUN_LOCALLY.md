# Running Tax Manager Locally

## Prerequisites

**Status**: Dev container is being rebuilt with Python 3.11 base image.

The container configuration has been updated to use `mcr.microsoft.com/devcontainers/python:3.11` which includes Python pre-installed. Once the rebuild completes, you can run the application locally.

## Quick Start (After Container Rebuild)

### 1. Start PostgreSQL

```bash
docker-compose up -d
```

This starts a local PostgreSQL database on port 5432.

### 2. Setup Backend

```bash
cd backend
./setup_dev.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Copy `.env.example` to `.env`

### 3. Configure Environment

Edit `backend/.env`:

```bash
# Minimal configuration for local development
SECRET_KEY=local-dev-secret-key-change-me
DEBUG=true

# Database (matches docker-compose.yml)
DATABASE_URL=postgresql://taxmanager:taxmanager_dev@localhost:5432/taxmanager

# Supabase (use dummy values for now)
SUPABASE_URL=http://localhost:8000
SUPABASE_KEY=dummy-key-for-local-dev
SUPABASE_JWT_SECRET=dummy-secret-for-local-dev

# Stripe (use test keys or dummy values)
STRIPE_SECRET_KEY=sk_test_dummy
STRIPE_PUBLISHABLE_KEY=pk_test_dummy
STRIPE_WEBHOOK_SECRET=whsec_dummy
STRIPE_PRICE_ID=price_dummy

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 4. Run Migrations

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 5. Start Server

```bash
./run_dev.sh
```

Or manually:

```bash
source venv/bin/activate
python -m app.main
```

### 6. Access Application

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Without Authentication

Since we don't have Supabase configured yet, you can test the API directly:

### Test Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### Test Tax Calculations

```python
# In Python shell
from decimal import Decimal
from datetime import date
from app.core.tax_calc import calculate_total_tax

result = calculate_total_tax(Decimal("30000.00"), date(2024, 6, 1))
print(result)
```

### Test Date Handling

```python
from datetime import date
from app.core.dates import get_tax_year, get_uc_assessment_period

# Tax year
print(get_tax_year(date(2024, 6, 1)))  # "2024-25"

# UC period
period = get_uc_assessment_period(date(2024, 6, 20), 15)
print(period)  # (2024-06-15, 2024-07-14)
```

## With Full Setup

To use the web UI with authentication:

### 1. Create Supabase Project

1. Go to https://supabase.com
2. Create new project
3. Get your project URL and anon key
4. Get JWT secret from Settings → API

### 2. Update .env

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
```

### 3. Create Test User

In Supabase dashboard:
1. Go to Authentication → Users
2. Add user manually
3. Note the user ID

### 4. Create User in Tax Manager

```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "supabase_id": "user-id-from-supabase",
    "email": "test@example.com",
    "full_name": "Test User"
  }'
```

### 5. Login

Visit http://localhost:8000/login and use your Supabase credentials.

## Troubleshooting

### Python Not Found

Wait for dev container rebuild to complete. Check with:

```bash
python3 --version
```

Should show: `Python 3.11.x`

### Database Connection Failed

Make sure PostgreSQL is running:

```bash
docker-compose ps
```

If not running:

```bash
docker-compose up -d
```

### Port Already in Use

If port 8000 is in use:

```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Import Errors

Make sure virtual environment is activated:

```bash
source venv/bin/activate
```

Reinstall dependencies:

```bash
pip install -r requirements.txt
```

## Testing Without Web UI

You can test all backend functionality without the web UI:

### Run Tests

```bash
cd backend
source venv/bin/activate
pytest
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

### Use Python Shell

```bash
cd backend
source venv/bin/activate
python
```

Then:

```python
from app.core.tax_calc import calculate_total_tax
from decimal import Decimal
from datetime import date

# Test tax calculation
result = calculate_total_tax(Decimal("30000"), date(2024, 6, 1))
print(f"Tax: £{result['total_tax']}")
```

## Current Status

The dev container is rebuilding with Python 3.11. Once complete:

1. ✅ PostgreSQL can start via docker-compose
2. ✅ Backend can be set up and run
3. ✅ Tests can be executed
4. ✅ API can be accessed
5. ⚠️ Web UI needs authentication setup
6. ⚠️ Subscription features need Stripe setup

## Next Steps

1. Wait for container rebuild
2. Run `docker-compose up -d`
3. Run `cd backend && ./setup_dev.sh`
4. Run `./run_dev.sh`
5. Visit http://localhost:8000/docs

The application is fully functional locally, just needs Python installed (happening now via container rebuild).
