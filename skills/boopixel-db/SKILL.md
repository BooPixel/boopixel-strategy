---
name: boopixel-db
description: Manipulate BooPixel production database (MySQL). Use when the user asks to query, update, insert, delete, or analyze data from the BooPixel business database (projects, charges, customers, subscriptions, transactions, leads, etc.).
version: 1.0.0
allowed-tools: Bash, Read, Grep, Glob
---

You are an expert assistant for managing the **BooPixel business database**. When the user asks to manipulate data, generate correct Python/SQLAlchemy code and execute it.

**Project:** /Users/fernandocelmer/Lab/BooPixel/business-api
**Database:** MySQL (credentials in `~/.env` as `DATABASE_URL`)

---

## Connection

Always connect using the DATABASE_URL from `~/.env`:

```python
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(os.path.expanduser("~/.env"))
engine = create_engine(os.environ["DATABASE_URL"])
```

---

## Database Schema (18 tables)

### Users & Companies

**users**
- `id` (UUID PK), `email` (unique), `password_hash`, `name`, `phone`, `document`
- `status` (active|inactive|prospect|blocked), `address` (JSON), `notes`, `is_active`

**companies**
- `id` (INT PK), `name`, `slug` (unique), `document` (unique), `email`, `phone`, `is_active`

**user_companies** (junction)
- `id`, `user_id` (FK), `company_id` (FK), `role` (admin|client), `is_owner`, `is_active`

**customer_emails**
- `id`, `user_id` (FK), `email`, `label`, `is_primary`

### Catalog

**service_types**
- `id`, `company_id`, `name`, `description`, `is_active`

**asset_types**
- `id`, `company_id`, `service_type_id` (FK), `name`, `description`, `is_active`

**offerings**
- `id`, `company_id`, `slug`, `name`, `service_type_id`
- `pricing_model` (one_time|recurring|hybrid)
- `price_from`, `setup_fee`, `recurring_price`, `is_active`, `is_featured`

**plans**
- `id`, `company_id`, `slug`, `name`, `tier`, `description`
- `price_monthly`, `price_yearly`, `trial_days`, `is_active`, `is_featured`

**plan_items** (bridge Plans <-> Offerings)
- `id`, `plan_id`, `offering_id`, `quantity`, `limit_note`

**discounts**
- `id`, `company_id`, `code`, `name`
- `type` (percent|fixed|months_free), `value`
- `applies_to` (plan|offering|any), `valid_from`, `valid_until`
- `max_uses`, `used_count`, `min_months`, `is_active`

### Projects & Subscriptions

**projects**
- `id`, `company_id`, `customer_id` (FK users UUID), `offering_id`, `discount_id`
- `name`, `setup_fee`, `recurring_price`
- `status` (proposal|in_progress|active|delivered|paid|archived)
- `started_at`, `delivered_at`, `notes`

**subscriptions**
- `id`, `company_id`, `customer_id`, `plan_id`, `discount_id`
- `billing_cycle` (monthly|yearly), `status` (trialing|active|paused|cancelled|expired)
- `price_override`, `started_at`, `current_period_end`, `ends_at`, `notes`

### Financial

**charges**
- `id`, `code` (indexed), `company_id`, `user_id`, `user_name`
- `project_id` (nullable), `value`, `description`
- `status` (pending|paid|overdue|cancelled), `method`, `due_date`, `paid_date`
- `is_recurring`, `installment_number`, `total_installments`, `notes`, `archived`

**transactions**
- `id`, `code` (indexed), `company_id`, `user_id`, `user_name`
- `charge_id` (nullable), `direction` (income|expense)
- `category` (revenue|salary|tax|fee|deposit|other), `value`
- `account`, `description`, `transaction_date`, `notes`, `archived`

### Service Assets

**service_assets**
- `id`, `project_id`, `company_id`, `asset_type_id`
- `provider`, `identifier`, `url`, `login_url`, `credentials` (encrypted)
- `cost`, `billing_cycle` (monthly|quarterly|yearly)
- `expires_at`, `auto_renew`, `status` (active|expiring_soon|expired|cancelled)

### Leads & Forms

**leads**
- `id`, `company_id`, `name`, `email`, `phone`, `message`, `source`
- `status` (new|contacted|qualified|converted|lost)
- `notes`, `converted_user_id` (FK), `created_at`, `updated_at`

**form_templates**
- `id`, `company_id`, `slug`, `name`, `description`
- `initial_step`, `steps` (JSON), `redirect_url`, `redirect_after_seconds`, `is_active`

### Invitations

**invites**
- `id`, `company_id`, `email`, `role` (operator|viewer), `token` (unique)
- `status` (pending|accepted|expired), `invited_by` (FK), `expires_at`

---

## Key Relationships

- User <-> Company: many-to-many via `user_companies`
- Company -> Plans, Offerings, Discounts, ServiceTypes, AssetTypes
- Plan <-> Offering: many-to-many via `plan_items`
- Project -> Customer (User), Company, Offering, Discount
- Subscription -> Customer (User), Plan, Discount
- Charge -> Company, User, Project
- Transaction -> Company, User, Charge
- ServiceAsset -> Company, Project, AssetType

---

## Rules

1. **Always use parameterized queries** — never concatenate user input into SQL
2. **Always commit** after INSERT/UPDATE/DELETE
3. **Always confirm destructive operations** (DELETE, bulk UPDATE) with the user before executing
4. **Read before update** — show current state before modifying
5. **Use transactions** for multi-table operations
6. **UUID fields** (user IDs) are stored as `binary(16)` — use `UNHEX(REPLACE(uuid, '-', ''))` for queries
7. **Timestamps** are in UTC

---

## Common Recipes

### List active projects
```python
conn.execute(text("SELECT id, name, status, setup_fee, recurring_price FROM projects WHERE status = 'active'"))
```

### List customers with company
```python
conn.execute(text("""
    SELECT u.name, u.email, uc.role, c.name as company
    FROM users u
    JOIN user_companies uc ON u.id = uc.user_id
    JOIN companies c ON uc.company_id = c.id
    WHERE uc.role = 'client'
"""))
```

### Revenue summary
```python
conn.execute(text("""
    SELECT SUM(value) as total, direction, category
    FROM transactions
    WHERE company_id = :cid AND archived = 0
    GROUP BY direction, category
"""), {"cid": company_id})
```

### Pending charges
```python
conn.execute(text("""
    SELECT id, code, user_name, value, due_date, description
    FROM charges
    WHERE status = 'pending' AND company_id = :cid
    ORDER BY due_date
"""), {"cid": company_id})
```
