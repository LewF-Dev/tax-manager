# Quick Start Guide

Get Tax Manager running locally in 5 minutes.

## Prerequisites

- Python 3.11+
- Docker (for PostgreSQL)
- Git

## Steps

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/your-org/tax-manager.git
cd tax-manager

# Start PostgreSQL
docker-compose up -d

# Setup backend
cd backend
./setup_dev.sh
source venv/bin/activate
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env
```

Edit `.env` with minimal configuration:

```bash
# Application
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=true

# Database (matches docker-compose.yml)
DATABASE_URL=postgresql://taxmanager:taxmanager_dev@localhost:5432/taxmanager

# Supabase (use test values for local dev)
SUPABASE_URL=http://localhost:8000
SUPABASE_KEY=test-key
SUPABASE_JWT_SECRET=test-secret

# Stripe (use test keys)
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_test
STRIPE_PRICE_ID=price_test

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 3. Initialize Database

```bash
# Run migrations
alembic upgrade head
```

### 4. Start Server

```bash
# Start development server
python -m app.main
```

Server runs at: `http://localhost:8000`

API docs at: `http://localhost:8000/docs`

## Test the API

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### View API Documentation

Open in browser: `http://localhost:8000/docs`

You'll see interactive API documentation with all endpoints.

## Next Steps

### Run Tests

```bash
pytest
```

### Create Test User

For local testing without Supabase:

```python
# In Python shell
from app.database import SessionLocal
from app.models.user import User
import uuid

db = SessionLocal()

user = User(
    supabase_id=str(uuid.uuid4()),
    email="test@example.com",
    full_name="Test User",
    subscription_status="active"
)

db.add(user)
db.commit()
print(f"Created user: {user.id}")
```

### Test Tax Calculations

```python
from decimal import Decimal
from datetime import date
from app.core.tax_calc import calculate_total_tax

# Calculate tax for £30,000 profit
result = calculate_total_tax(Decimal("30000.00"), date(2024, 6, 1))
print(result)
```

Expected output:
```python
{
    'income_tax': 3486.0,
    'ni_class2': 179.4,
    'ni_class4': 1568.7,
    'total_tax': 5234.1,
    'tax_year': '2024-25',
    'ruleset_version': '2024-25-v1'
}
```

### Test UC Period Calculation

```python
from datetime import date
from app.core.dates import get_uc_assessment_period

# Get UC period for June 20, 2024 with assessment day 15
period_start, period_end = get_uc_assessment_period(
    date(2024, 6, 20),
    15
)

print(f"Period: {period_start} to {period_end}")
```

Expected output:
```
Period: 2024-06-15 to 2024-07-14
```

## Common Issues

### Port Already in Use

If port 8000 is in use:

```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Database Connection Failed

Check PostgreSQL is running:

```bash
docker-compose ps
```

If not running:

```bash
docker-compose up -d
```

### Import Errors

Ensure virtual environment is activated:

```bash
source venv/bin/activate
```

Reinstall dependencies:

```bash
pip install -r requirements.txt
```

## Development Workflow

### Making Changes

1. Create feature branch
   ```bash
   git checkout -b feature/your-feature
   ```

2. Make changes

3. Run tests
   ```bash
   pytest
   ```

4. Commit changes
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

5. Push and create PR
   ```bash
   git push origin feature/your-feature
   ```

### Database Changes

1. Modify models in `app/models/`

2. Create migration
   ```bash
   alembic revision --autogenerate -m "Description"
   ```

3. Review migration file in `alembic/versions/`

4. Apply migration
   ```bash
   alembic upgrade head
   ```

### Adding Tests

Add tests to `tests/` directory:

```python
# tests/test_new_feature.py
def test_new_feature():
    """Test new feature."""
    result = new_feature()
    assert result == expected
```

Run specific test:
```bash
pytest tests/test_new_feature.py
```

## Useful Commands

```bash
# Run tests with coverage
pytest --cov=app --cov-report=html

# Format code
black app/ tests/

# Check code style
flake8 app/ tests/

# View database
docker exec -it taxmanager-db psql -U taxmanager

# View logs
docker-compose logs -f

# Reset database
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

## Resources

- [Full Documentation](README.md)
- [API Documentation](http://localhost:8000/docs)
- [Contributing Guide](CONTRIBUTING.md)
- [Deployment Guide](DEPLOYMENT.md)

## Getting Help

- Check [existing issues](https://github.com/your-org/tax-manager/issues)
- Review [documentation](README.md)
- Ask in [discussions](https://github.com/your-org/tax-manager/discussions)

## What's Next?

- Read the [full README](README.md) for detailed information
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Explore the [API documentation](http://localhost:8000/docs)
