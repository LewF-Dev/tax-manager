# API Usage Examples

Real-world examples of using the Tax Manager API.

## Authentication

All requests (except `/health` and webhooks) require a JWT token from Supabase Auth.

```bash
# Include in Authorization header
Authorization: Bearer <your-jwt-token>
```

## User Management

### Create User Account

After Supabase authentication, create user in Tax Manager:

```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "supabase_id": "user-uuid-from-supabase",
    "email": "user@example.com",
    "full_name": "John Smith"
  }'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Smith",
  "trading_start_date": null,
  "uc_enabled": false,
  "uc_assessment_day": null,
  "tax_set_aside_percentage": 20.00,
  "subscription_status": "inactive",
  "stripe_customer_id": null
}
```

### Update User Profile

Set trading start date and enable UC:

```bash
curl -X PATCH http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "trading_start_date": "2024-06-01",
    "uc_enabled": true,
    "uc_assessment_day": 15,
    "tax_set_aside_percentage": 25.00
  }'
```

## Income Tracking

### Add Income Transaction

```bash
curl -X POST http://localhost:8000/api/v1/income/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "date_received": "2024-06-15",
    "amount": 1500.00,
    "description": "Website development project"
  }'
```

Response:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "date_received": "2024-06-15",
  "amount": 1500.00,
  "description": "Website development project",
  "tax_year": "2024-25",
  "tax_ruleset_version": "2024-25-v1",
  "created_at": "2024-06-15T10:30:00Z"
}
```

### List Income Transactions

```bash
# All income
curl http://localhost:8000/api/v1/income/ \
  -H "Authorization: Bearer <token>"

# Filter by tax year
curl http://localhost:8000/api/v1/income/?tax_year=2024-25 \
  -H "Authorization: Bearer <token>"
```

### Update Income Transaction

```bash
curl -X PATCH http://localhost:8000/api/v1/income/660e8400-e29b-41d4-a716-446655440001 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1600.00,
    "description": "Website development project (updated)"
  }'
```

### Delete Income Transaction

```bash
curl -X DELETE http://localhost:8000/api/v1/income/660e8400-e29b-41d4-a716-446655440001 \
  -H "Authorization: Bearer <token>"
```

## Expense Tracking

### Get Expense Categories

```bash
curl http://localhost:8000/api/v1/expenses/categories \
  -H "Authorization: Bearer <token>"
```

Response:
```json
[
  "Equipment",
  "Software",
  "Travel",
  "Office Supplies",
  "Professional Fees",
  "Marketing",
  "Training",
  "Insurance",
  "Other"
]
```

### Add Expense Transaction

```bash
curl -X POST http://localhost:8000/api/v1/expenses/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "date_paid": "2024-06-10",
    "amount": 49.99,
    "category": "Software",
    "description": "Adobe Creative Cloud subscription"
  }'
```

### List Expenses

```bash
# All expenses
curl http://localhost:8000/api/v1/expenses/ \
  -H "Authorization: Bearer <token>"

# Filter by tax year
curl http://localhost:8000/api/v1/expenses/?tax_year=2024-25 \
  -H "Authorization: Bearer <token>"
```

## Tax Calculations

### Get Tax Summary

```bash
# Current tax year
curl http://localhost:8000/api/v1/tax/summary \
  -H "Authorization: Bearer <token>"

# Specific tax year
curl http://localhost:8000/api/v1/tax/summary?tax_year=2023-24 \
  -H "Authorization: Bearer <token>"
```

Response:
```json
{
  "tax_year": "2024-25",
  "tax_year_start": "2024-04-06",
  "tax_year_end": "2025-04-05",
  "total_income": 15000.00,
  "total_expenses": 2500.00,
  "net_profit": 12500.00,
  "income_tax": 0.00,
  "ni_class2": 179.40,
  "ni_class4": 0.00,
  "total_tax": 179.40,
  "tax_to_set_aside": 3750.00,
  "hmrc_registration_deadline": "2025-10-05",
  "vat_threshold_proximity": 17.65
}
```

### Create Tax Snapshot

Save a point-in-time calculation:

```bash
curl -X POST http://localhost:8000/api/v1/tax/snapshots?tax_year=2024-25 \
  -H "Authorization: Bearer <token>"
```

### List Tax Snapshots

```bash
curl http://localhost:8000/api/v1/tax/snapshots \
  -H "Authorization: Bearer <token>"
```

## Universal Credit (if enabled)

### Get Current UC Period

```bash
curl http://localhost:8000/api/v1/uc/current-period \
  -H "Authorization: Bearer <token>"
```

Response:
```json
{
  "period_start": "2024-06-15",
  "period_end": "2024-07-14",
  "total_income": 1500.00,
  "total_expenses": 150.00,
  "net_profit": 1350.00,
  "reported_at": null,
  "notes": null
}
```

### Generate UC Report

Create snapshot for a specific period:

```bash
curl -X POST "http://localhost:8000/api/v1/uc/periods/generate?period_start_date=2024-06-15" \
  -H "Authorization: Bearer <token>"
```

### Mark Period as Reported

After reporting to UC:

```bash
curl -X PATCH http://localhost:8000/api/v1/uc/periods/2024-06-15/mark-reported \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "reported_at": "2024-07-01",
    "notes": "Reported via UC online account"
  }'
```

### List UC Periods

```bash
# Last 12 periods
curl http://localhost:8000/api/v1/uc/periods \
  -H "Authorization: Bearer <token>"

# Custom limit
curl http://localhost:8000/api/v1/uc/periods?limit=6 \
  -H "Authorization: Bearer <token>"
```

## Data Export

### Export Transactions as CSV

```bash
curl http://localhost:8000/api/v1/export/csv \
  -H "Authorization: Bearer <token>" \
  -o transactions.csv
```

CSV format:
```csv
Type,Date,Amount,Description,Category,Tax Year,Created At
Income,2024-06-15,1500.00,Website development project,,2024-25,2024-06-15T10:30:00Z
Expense,2024-06-10,49.99,Adobe Creative Cloud,Software,2024-25,2024-06-10T09:15:00Z
```

### Export Full Data (GDPR)

```bash
curl http://localhost:8000/api/v1/export/full \
  -H "Authorization: Bearer <token>" \
  -o full_export.json
```

JSON includes:
- User profile
- All income transactions
- All expense transactions
- All UC reports
- All tax snapshots

## Billing & Subscriptions

### Create Checkout Session

Start subscription process:

```bash
curl -X POST http://localhost:8000/api/v1/billing/create-checkout-session \
  -H "Authorization: Bearer <token>"
```

Response:
```json
{
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_..."
}
```

Redirect user to `checkout_url`.

### Create Customer Portal Session

For subscription management:

```bash
curl -X POST http://localhost:8000/api/v1/billing/create-portal-session \
  -H "Authorization: Bearer <token>"
```

Response:
```json
{
  "portal_url": "https://billing.stripe.com/p/session/..."
}
```

Redirect user to `portal_url` to manage subscription.

## Common Workflows

### New User Onboarding

1. User signs up via Supabase Auth
2. Create user in Tax Manager
3. User sets trading start date
4. User subscribes via Stripe
5. User starts tracking income/expenses

```bash
# 1. Supabase handles authentication
# 2. Create user
curl -X POST http://localhost:8000/api/v1/users/ ...

# 3. Set trading start date
curl -X PATCH http://localhost:8000/api/v1/users/me \
  -d '{"trading_start_date": "2024-06-01"}'

# 4. Create checkout session
curl -X POST http://localhost:8000/api/v1/billing/create-checkout-session

# 5. User adds transactions
curl -X POST http://localhost:8000/api/v1/income/ ...
```

### Monthly UC Reporting

1. Get current period summary
2. Review income and expenses
3. Generate UC report
4. Report to UC
5. Mark as reported in system

```bash
# 1. Get current period
curl http://localhost:8000/api/v1/uc/current-period

# 2. Review transactions (if needed)
curl http://localhost:8000/api/v1/income/?tax_year=2024-25
curl http://localhost:8000/api/v1/expenses/?tax_year=2024-25

# 3. Generate report
curl -X POST "http://localhost:8000/api/v1/uc/periods/generate?period_start_date=2024-06-15"

# 4. User reports to UC manually

# 5. Mark as reported
curl -X PATCH http://localhost:8000/api/v1/uc/periods/2024-06-15/mark-reported \
  -d '{"reported_at": "2024-07-01"}'
```

### End of Tax Year

1. Get tax summary
2. Create tax snapshot
3. Export all data
4. Prepare for Self Assessment

```bash
# 1. Get summary
curl http://localhost:8000/api/v1/tax/summary?tax_year=2024-25

# 2. Create snapshot
curl -X POST http://localhost:8000/api/v1/tax/snapshots?tax_year=2024-25

# 3. Export data
curl http://localhost:8000/api/v1/export/csv -o tax_year_2024-25.csv
curl http://localhost:8000/api/v1/export/full -o full_data_2024-25.json

# 4. Use exported data for Self Assessment
```

## Error Handling

### Validation Error

```bash
curl -X POST http://localhost:8000/api/v1/income/ \
  -d '{"amount": -100}'  # Invalid: negative amount
```

Response (422):
```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### Authentication Error

```bash
curl http://localhost:8000/api/v1/income/
# Missing Authorization header
```

Response (401):
```json
{
  "detail": "Not authenticated"
}
```

### Subscription Required

```bash
curl http://localhost:8000/api/v1/income/ \
  -H "Authorization: Bearer <token>"
# User has no active subscription
```

Response (403):
```json
{
  "detail": "Active subscription required"
}
```

### UC Not Enabled

```bash
curl http://localhost:8000/api/v1/uc/current-period \
  -H "Authorization: Bearer <token>"
# User has uc_enabled=false
```

Response (403):
```json
{
  "detail": "Universal Credit functionality is not enabled for this account"
}
```

## Testing with curl

### Set Token Variable

```bash
export TOKEN="your-jwt-token-here"
```

Then use in requests:
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Pretty Print JSON

```bash
curl http://localhost:8000/api/v1/tax/summary \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Save Response

```bash
curl http://localhost:8000/api/v1/tax/summary \
  -H "Authorization: Bearer $TOKEN" \
  -o tax_summary.json
```

## Interactive API Documentation

Visit `http://localhost:8000/docs` for:
- Interactive API explorer
- Request/response schemas
- Try endpoints directly
- Authentication setup

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Add income
response = requests.post(
    f"{BASE_URL}/income/",
    headers=headers,
    json={
        "date_received": "2024-06-15",
        "amount": 1500.00,
        "description": "Website project"
    }
)
income = response.json()
print(f"Created income: {income['id']}")

# Get tax summary
response = requests.get(
    f"{BASE_URL}/tax/summary",
    headers=headers
)
summary = response.json()
print(f"Total tax: £{summary['total_tax']}")
```

## JavaScript Client Example

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';
const TOKEN = 'your-jwt-token';

const headers = {
  'Authorization': `Bearer ${TOKEN}`,
  'Content-Type': 'application/json'
};

// Add income
const response = await fetch(`${BASE_URL}/income/`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    date_received: '2024-06-15',
    amount: 1500.00,
    description: 'Website project'
  })
});
const income = await response.json();
console.log('Created income:', income.id);

// Get tax summary
const summaryResponse = await fetch(`${BASE_URL}/tax/summary`, { headers });
const summary = await summaryResponse.json();
console.log('Total tax:', summary.total_tax);
```
