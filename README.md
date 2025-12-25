# Tax Manager

A SaaS application for UK self-employed individuals to manage income, expenses, tax obligations, and Universal Credit reporting with clean compliance and zero ambiguity.

## Philosophy

This app is built around one core principle: **UC ending because income goes up is the success condition, not a failure state.**

The system enforces:
- Clean compliance with HMRC and UC rules
- Clear reporting with no ambiguity
- Automatic tax discipline
- Cash-basis accounting only
- Zero tolerance for "forgetting" obligations

## Features

### Core Functionality
- **Income Tracking**: Cash-received basis only, with automatic tax year assignment
- **Expense Tracking**: Cash-paid basis with categorization
- **Tax Calculations**: Automatic calculation using versioned UK tax rulesets
- **Tax Discipline**: Immediate calculation of tax to set aside (default 20%, adjustable)
- **HMRC Timeline**: Registration deadline tracking based on trading start date
- **VAT Monitoring**: Threshold proximity warnings

### Universal Credit (Optional)
- Monthly assessment period tracking
- Cash-basis reporting aligned with UC rules
- Period-by-period snapshots
- £0 months cannot be skipped
- UC functionality completely isolated when not enabled

### Data & Compliance
- CSV export of all transactions
- Full data export (GDPR compliance)
- User-initiated account deletion
- Audit trail via tax snapshots
- Multi-year tax ruleset support

### Subscription
- Stripe-powered monthly subscriptions
- Customer portal for self-service management
- Automated billing lifecycle

## Architecture

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: Supabase Auth (JWT)
- **Payments**: Stripe
- **Validation**: Pydantic v2

### Key Design Decisions

1. **Tax Ruleset Versioning**: Every transaction uses the correct tax ruleset based on its date, supporting backdated entries and historical accuracy.

2. **UC Isolation**: Universal Credit functionality is completely optional and isolated behind a feature flag. Users not on UC never see UC-related features.

3. **Multi-tenancy**: All queries are filtered by `user_id` at the application layer, with plans for row-level security.

4. **Audit Trail**: Tax calculations are stored as snapshots with the ruleset version used, enabling historical accuracy even when rules change.

5. **Cash Basis Only**: No accrual accounting. If money didn't hit the account, it doesn't exist yet.

## Project Structure

```
tax-manager/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Core logic (dates, tax, config)
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic (Stripe, exports)
│   │   ├── templates/       # HTML templates (future)
│   │   └── main.py          # FastAPI app
│   ├── alembic/             # Database migrations
│   ├── tests/               # Test suite
│   └── requirements.txt
└── README.md
```

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL (or Supabase)
- Supabase account (for auth)
- Stripe account (for payments)

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Application
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/taxmanager

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...
```

### Installation

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
python -m app.main
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Running Tests

```bash
pytest
```

## API Endpoints

### Authentication
All endpoints except `/health` and `/billing/webhook` require JWT authentication via `Authorization: Bearer <token>` header.

### Users
- `POST /api/v1/users/` - Create user account
- `GET /api/v1/users/me` - Get current user profile
- `PATCH /api/v1/users/me` - Update user profile
- `DELETE /api/v1/users/me` - Delete account (GDPR)

### Income
- `POST /api/v1/income/` - Create income transaction
- `GET /api/v1/income/` - List income transactions
- `GET /api/v1/income/{id}` - Get specific transaction
- `PATCH /api/v1/income/{id}` - Update transaction
- `DELETE /api/v1/income/{id}` - Delete transaction

### Expenses
- `GET /api/v1/expenses/categories` - List expense categories
- `POST /api/v1/expenses/` - Create expense transaction
- `GET /api/v1/expenses/` - List expense transactions
- `GET /api/v1/expenses/{id}` - Get specific transaction
- `PATCH /api/v1/expenses/{id}` - Update transaction
- `DELETE /api/v1/expenses/{id}` - Delete transaction

### Tax
- `GET /api/v1/tax/summary` - Get tax summary for current/specified year
- `POST /api/v1/tax/snapshots` - Create tax snapshot
- `GET /api/v1/tax/snapshots` - List tax snapshots

### Universal Credit (requires `uc_enabled=true`)
- `GET /api/v1/uc/current-period` - Get current UC assessment period
- `GET /api/v1/uc/periods` - List UC periods
- `POST /api/v1/uc/periods/generate` - Generate UC report
- `PATCH /api/v1/uc/periods/{date}/mark-reported` - Mark period as reported

### Export
- `GET /api/v1/export/csv` - Export transactions as CSV
- `GET /api/v1/export/full` - Full data export (JSON)

### Billing
- `POST /api/v1/billing/create-checkout-session` - Create Stripe checkout
- `POST /api/v1/billing/create-portal-session` - Create customer portal
- `POST /api/v1/billing/webhook` - Stripe webhook handler

## Tax Rulesets

Tax rulesets are versioned by UK tax year in `app/core/tax_rulesets.py`. Currently supported:
- 2023-24
- 2024-25
- 2025-26 (placeholder, update when rates announced)

Each ruleset includes:
- Personal allowance
- Income tax rates and thresholds
- National Insurance Class 2 and Class 4 rates
- VAT thresholds

## Deployment

### Recommended Stack
- **Database**: Supabase (Postgres + Auth)
- **API Hosting**: Render or Railway
- **Monitoring**: Sentry
- **Payments**: Stripe

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Stripe Webhook Setup

1. Create webhook endpoint in Stripe Dashboard
2. Point to `https://your-domain.com/api/v1/billing/webhook`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy webhook secret to `STRIPE_WEBHOOK_SECRET`

## Testing

The test suite covers:
- Tax calculation accuracy across different profit levels
- UK tax year boundary handling
- UC assessment period calculations
- Multi-year ruleset support

Run tests with coverage:
```bash
pytest --cov=app --cov-report=html
```

## Roadmap

### v1.0 (Current)
- ✅ Core income/expense tracking
- ✅ Tax calculations with ruleset versioning
- ✅ UC reporting (optional)
- ✅ Stripe subscriptions
- ✅ Data exports
- ✅ API-first architecture

### v1.1 (Planned)
- Web UI (HTMX + Tailwind)
- Dashboard with key metrics
- Onboarding flow
- Email notifications

### v1.2 (Future)
- Mobile app (React Native/Flutter)
- Historical year comparison views
- Enhanced reporting
- AI support integration

## License

Proprietary - All rights reserved

## Support

For support inquiries, contact: [support email]
