# Contributing to Tax Manager

## Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/tax-manager.git
   cd tax-manager
   ```

2. **Start PostgreSQL** (using Docker)
   ```bash
   docker-compose up -d
   ```

3. **Set up backend**
   ```bash
   cd backend
   ./setup_dev.sh
   source venv/bin/activate
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

5. **Run migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start development server**
   ```bash
   python -m app.main
   ```

   API will be available at `http://localhost:8000`
   
   API docs at `http://localhost:8000/docs`

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tax_calc.py

# Run specific test
pytest tests/test_tax_calc.py::TestTaxCalculations::test_income_tax_basic_rate
```

## Code Standards

### Python Style
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes

### Naming Conventions
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Example
```python
from decimal import Decimal
from typing import Dict, Any


def calculate_tax(profit: Decimal, ruleset: Dict[str, Any]) -> Decimal:
    """
    Calculate tax on profit using specified ruleset.
    
    Args:
        profit: Net profit amount
        ruleset: Tax ruleset dictionary
        
    Returns:
        Tax amount
    """
    if profit <= 0:
        return Decimal("0.00")
    
    # Implementation...
    return tax_amount
```

## Project Structure

### Core Principles

1. **Separation of Concerns**
   - `models/`: Database models only
   - `schemas/`: Pydantic validation schemas
   - `core/`: Business logic (tax calculations, date handling)
   - `services/`: External integrations (Stripe, exports)
   - `api/`: HTTP endpoints

2. **Tax Ruleset Versioning**
   - All tax calculations must use versioned rulesets
   - Never hardcode tax rates
   - Always determine ruleset from transaction date

3. **Multi-tenancy**
   - All queries must filter by `user_id`
   - Never expose data across users
   - Test isolation thoroughly

4. **UC Isolation**
   - UC functionality behind `uc_enabled` flag
   - UC routes require `require_uc_enabled` dependency
   - Non-UC users never see UC features

## Adding Features

### New Tax Calculation

1. Add function to `app/core/tax_calc.py`
2. Use ruleset parameter, never hardcode rates
3. Return `Decimal` for money values
4. Add comprehensive tests

Example:
```python
def calculate_new_tax(profit: Decimal, ruleset: Dict[str, Any]) -> Decimal:
    """Calculate new tax type."""
    threshold = Decimal(str(ruleset["new_threshold"]))
    rate = Decimal(str(ruleset["new_rate"]))
    
    if profit <= threshold:
        return Decimal("0.00")
    
    taxable = profit - threshold
    return (taxable * rate).quantize(Decimal("0.01"))
```

### New API Endpoint

1. Add route to appropriate router in `app/api/v1/`
2. Use dependency injection for auth and DB
3. Add Pydantic schemas for request/response
4. Document with docstring
5. Add tests

Example:
```python
@router.get("/summary", response_model=SummaryResponse)
async def get_summary(
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Get user summary."""
    # Implementation
    return summary
```

### New Database Model

1. Add model to `app/models/`
2. Inherit from `Base` and `TimestampMixin`
3. Include `user_id` foreign key
4. Add relationship to `User` model
5. Create migration
6. Add Pydantic schemas

Example:
```python
class NewModel(Base, TimestampMixin):
    """Description of model."""
    __tablename__ = "new_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Fields...
    
    user = relationship("User", back_populates="new_models")
```

Then create migration:
```bash
alembic revision --autogenerate -m "Add new_models table"
# Review and edit migration file
alembic upgrade head
```

## Testing Guidelines

### Test Structure

```python
class TestFeature:
    """Test feature description."""
    
    def test_normal_case(self):
        """Test normal operation."""
        # Arrange
        input_data = ...
        
        # Act
        result = function(input_data)
        
        # Assert
        assert result == expected
    
    def test_edge_case(self):
        """Test edge case."""
        # ...
    
    def test_error_case(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            function(invalid_input)
```

### What to Test

1. **Tax Calculations**
   - All rate bands
   - Threshold boundaries
   - Zero/negative inputs
   - Different tax years

2. **Date Handling**
   - Tax year boundaries (April 5/6)
   - UC period calculations
   - Year-end edge cases

3. **API Endpoints**
   - Success cases
   - Validation errors
   - Authentication/authorization
   - Multi-tenancy isolation

4. **Business Logic**
   - Ruleset selection
   - UC period generation
   - Export formatting

### Test Coverage

Aim for:
- Core logic: 100%
- API endpoints: 90%+
- Overall: 85%+

## Database Migrations

### Creating Migrations

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Description of change"

# Review generated file in alembic/versions/
# Edit if needed (Alembic doesn't catch everything)

# Test migration
alembic upgrade head

# Test rollback
alembic downgrade -1
alembic upgrade head
```

### Migration Best Practices

1. **One logical change per migration**
2. **Always test rollback**
3. **Never edit existing migrations** (create new one)
4. **Add data migrations separately** from schema changes
5. **Test with production-like data volume**

### Migration Checklist

- [ ] Migration runs successfully
- [ ] Rollback works correctly
- [ ] No data loss
- [ ] Indexes added for foreign keys
- [ ] Nullable fields have defaults or migration data
- [ ] Tested with existing data

## Pull Request Process

### Before Submitting

1. **Run tests**
   ```bash
   pytest
   ```

2. **Check code style**
   ```bash
   # Install tools
   pip install black isort flake8
   
   # Format code
   black app/ tests/
   isort app/ tests/
   
   # Check style
   flake8 app/ tests/
   ```

3. **Update documentation** if needed

4. **Test manually** in development environment

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

### Review Process

1. Automated checks must pass
2. At least one approval required
3. All comments addressed
4. Squash and merge

## Updating Tax Rulesets

When HMRC announces new rates (usually in March):

1. **Add new ruleset** to `app/core/tax_rulesets.py`
   ```python
   "2026-27": {
       "version": "2026-27-v1",
       "personal_allowance": 12570,  # Update with new rates
       # ...
   }
   ```

2. **Add tests** for new tax year
   ```python
   def test_tax_calculation_2026_27(self):
       """Test calculations for 2026-27 tax year."""
       result = calculate_total_tax(
           Decimal("30000.00"),
           date(2026, 6, 1)
       )
       assert result["tax_year"] == "2026-27"
       # Verify calculations with new rates
   ```

3. **Update documentation** if rates changed significantly

4. **Announce to users** via email/notification

## Common Issues

### Import Errors

Ensure you're in the virtual environment:
```bash
source venv/bin/activate
```

### Database Connection Errors

Check PostgreSQL is running:
```bash
docker-compose ps
```

Verify DATABASE_URL in `.env`

### Migration Conflicts

If multiple migrations created:
```bash
# Merge migrations
alembic merge heads -m "Merge migrations"
```

### Test Failures

Run single test with verbose output:
```bash
pytest -vv tests/test_file.py::test_name
```

## Getting Help

- Check existing issues
- Review documentation
- Ask in discussions
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
