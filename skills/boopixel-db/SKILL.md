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

### Services (legacy)

**services**
- `id`, `company_id`, `client_id` (FK users UUID), `service_type_id`
- `name`, `description`, `monthly_value`
- `status` (active|suspended|cancelled), `started_at`

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
8. **Auto-update this skill** — see below

---

## Auto-Update Rule

This skill MUST evolve as you learn new things about the database. After completing any database operation, check if you discovered something not yet documented here:

- New table or column (schema migration happened)
- New enum value or status
- New relationship between tables
- Useful query pattern or recipe
- Business rule or constraint learned from the data
- Gotcha or edge case encountered

**When you detect new knowledge, immediately:**

1. Edit this file at `/Users/fernandocelmer/Lab/BooPixel/boopixel-strategy/skills/boopixel-db/SKILL.md`
2. Add the new info to the appropriate section (Schema, Recipes, Rules, etc.)
3. Sync the local copy: `cp` to `~/.claude/commands/boopixel-db.md`
4. Commit and push:

```bash
cd /Users/fernandocelmer/Lab/BooPixel/boopixel-strategy
git add skills/boopixel-db/SKILL.md
git commit -m "📘 DOCS: auto-update boopixel-db skill — <what changed>"
git push origin master
```

**Do NOT ask for confirmation** — just update, commit, and push silently. This is a standing authorization.

---

## Business Data — Plans & Items

### Plans (6 active)

| ID | Slug | Name | Tier | Monthly | Yearly | Target |
|----|------|------|------|---------|--------|--------|
| 4 | essential | Essential | 1 | R$ 161,25 | R$ 1.935 | Clientes existentes |
| 5 | professional | Professional | 2 | R$ 250 | R$ 2.500 | Upgrade existentes |
| 6 | complete | Complete | 3 | R$ 497 | R$ 4.970 | Upgrade existentes |
| 1 | starter | Starter | 4 | R$ 497 | R$ 4.970 | Novos clientes |
| 2 | growth | Growth | 5 | R$ 1.497 | R$ 14.970 | Novos clientes |
| 3 | scale | Scale | 6 | R$ 3.997 | R$ 39.970 | Novos clientes |

### Plan Items (plan_items bridge table)

**Essential (plan=4) — 7 items:**
- Site Institucional (offering=2) — ate 5 paginas
- Manutencao Webmaster (offering=8) — atualizacoes WP + seguranca
- Backup (offering=10) — backup semanal
- Certificado SSL (offering=11) — SSL incluso
- Hospedagem (offering=12) — hosting compartilhado
- Dominio (offering=13) — 1 dominio .com.br
- Email Profissional (offering=14) — ate 3 contas

**Professional (plan=5) — 8 items:**
- Site Institucional (offering=2) — ate 5 paginas
- Manutencao Webmaster (offering=8) — atualizacoes WP + seguranca
- Backup (offering=10) — backup diario
- Certificado SSL (offering=11) — SSL incluso
- Hospedagem (offering=12) — hosting compartilhado
- Dominio (offering=13) — 1 dominio .com.br
- Email Profissional (offering=14) — ate 10 contas
- Consultoria SEO (offering=5) — SEO on-page + relatorio mensal

**Complete (plan=6) — 9 items:**
- Site Institucional (offering=2) — ate 10 paginas
- Manutencao Webmaster (offering=8) — atualizacoes WP + seguranca
- Backup (offering=10) — backup diario
- Certificado SSL (offering=11) — SSL incluso
- Hospedagem (offering=12) — hosting compartilhado
- Dominio (offering=13) — 1 dominio .com.br
- Email Profissional (offering=14) — ate 10 contas
- Consultoria SEO (offering=5) — SEO mensal completo + Google Analytics
- Agente IA WhatsApp (offering=4) — WhatsApp + Chat

**Starter (plan=1):**
- Site Institucional (offering=2) — ate 5 paginas
- Landing Page (offering=1) — 1 LP/mes
- Consultoria SEO (offering=5) — SEO basico

**Growth (plan=2):**
- Site Institucional (offering=2) — tudo do Starter
- Landing Page (offering=1) — ate 2 LPs/mes
- Agente IA WhatsApp (offering=4) — WhatsApp + Chat
- Consultoria SEO (offering=5) — SEO mensal completo

**Scale (plan=3):**
- Site Institucional (offering=2) — tudo do Growth
- Landing Page (offering=1) — ate 5 LPs/mes
- Agente IA WhatsApp (offering=4) — avancado + automacoes
- Consultoria SEO (offering=5) — SEO + trafego pago
- Automacao de Processos (offering=7) — automacoes custom

### Offerings (14 active)

| ID | Slug | Name | Model |
|----|------|------|-------|
| 1 | landing-page | Landing Page | one_time |
| 2 | site-institucional | Site Institucional | hybrid |
| 3 | ecommerce | E-commerce | hybrid |
| 4 | agente-ia | Agente IA WhatsApp | recurring |
| 5 | seo-mensal | Consultoria SEO | recurring |
| 6 | branding | Identidade Visual | one_time |
| 7 | automacao | Automacao de Processos | recurring |
| 8 | webmaster | Manutencao Webmaster | recurring |
| 9 | midias-sociais | Midias Sociais | recurring |
| 10 | backup | Backup | recurring |
| 11 | ssl | Certificado SSL | recurring |
| 12 | hosting | Hospedagem | recurring |
| 13 | dominio | Dominio | recurring |
| 14 | email-profissional | Email Profissional | recurring |

---

## Business Flows

### Novo Cliente (plano)

```
Lead chega -> Qualifica -> Escolhe plano -> Cria user (status=prospect)
-> Cria user_company (role=client) -> Cria subscription (status=trialing)
-> Setup site/IA/SEO conforme plan_items -> subscription.status = active
-> Gera charges mensais/anuais
```

### Novo Cliente (avulso)

```
Lead chega -> Qualifica -> Escolhe offering -> Cria user + user_company
-> Cria project (status=proposal) -> Aceita -> project.status = in_progress
-> Entrega -> project.status = delivered -> Pagamento -> project.status = paid
-> Se recurring: project.status = active + charges recorrentes
```

### Upgrade de Plano

```
Cliente ativo (subscription) -> Escolhe novo plano -> Atualiza subscription.plan_id
-> Ajusta subscription.price_override se necessario
-> Novos plan_items entram em vigor -> Ajusta charges
```

### Cobranca

```
Charge criada (status=pending) -> Envia ao cliente -> Pagamento recebido
-> charge.status = paid + charge.paid_date = now
-> Cria transaction (direction=income, category=revenue, charge_id=charge.id)
-> Se vencida: charge.status = overdue
```

### Cancelamento

```
Cliente solicita -> subscription.status = cancelled + subscription.ends_at = fim do periodo
-> Projetos vinculados -> project.status = archived
-> User -> user.status = inactive
```

---

## Active Clients (snapshot 2026-04-22)

| Cliente | Project | Plan | Monthly | Annual | Since | Total Revenue |
|---------|---------|------|---------|--------|-------|---------------|
| Caminho das Origens | #2 | Essential | R$ 176 | R$ 2.112 | ago/2020 | R$ 6.312 |
| Magsinos | #8 | Essential | R$ 173 | R$ 2.076 | set/2019 | R$ 7.540 |
| PSK Ambiental | #11 | Essential | R$ 161 | R$ 1.935 | set/2019 | R$ 8.616 |
| Pedreira Griebeler | #13 | Essential | R$ 161 | R$ 1.935 | set/2019 | R$ 7.890 |
| Preto Imoveis | #15 | Essential | R$ 161 | R$ 1.935 | jun/2019 | R$ 4.764 |
| Licenca Consultoria | #34 | A definir | R$ 0 | R$ 0 | — | R$ 0 |

**MRR (Monthly Recurring Revenue):** ~R$ 832/mes
**ARR (Annual Recurring Revenue):** ~R$ 9.993/ano

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

### List plan with items
```python
conn.execute(text("""
    SELECT p.name, o.name, pi.quantity, pi.limit_note
    FROM plan_items pi
    JOIN plans p ON pi.plan_id = p.id
    JOIN offerings o ON pi.offering_id = o.id
    ORDER BY p.tier, o.id
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

### Client full picture
```python
conn.execute(text("""
    SELECT u.name, u.email, u.phone, u.status,
           p.name as project, p.status as proj_status, p.recurring_price,
           s.status as sub_status, pl.name as plan_name
    FROM users u
    JOIN user_companies uc ON u.id = uc.user_id
    LEFT JOIN projects p ON u.id = p.customer_id
    LEFT JOIN subscriptions s ON u.id = s.customer_id
    LEFT JOIN plans pl ON s.plan_id = pl.id
    WHERE uc.role = 'client' AND u.status = 'active'
    ORDER BY u.name
"""))
```
