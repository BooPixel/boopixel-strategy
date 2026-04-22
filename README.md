# BooPixel Strategy

Strategic documentation, system modeling and skills for **BooPixel** — https://app.boopixel.com/

---

## Documents

### Business

| Document | Description |
|----------|-------------|
| [Pricing](pricing.md) | Plans (Essential, Professional, Complete, Starter, Growth, Scale, AI Agent), offerings, margins, market reference, active clients |
| [CNPJ LTDA](cnpj-ltda.md) | Abertura de CNPJ Sociedade Limitada entre Mateus e Fernando — checklist, custos, contabilidade, fluxo mermaid |
| [Project Overview](project-overview.md) | Visao geral do projeto BooPixel |

### Product

| Document | Description |
|----------|-------------|
| [Financial System](financial-system.md) | Data modeling, signup flow, business rules and strategy for the multi-tenant financial management system |
| [Lead Capture Forms](lead-capture-forms.md) | Conversational form strategy, personas, copy patterns, pipeline and roadmap for lead generation ([`forms/`](forms/)) |

---

## Skills

Skills instalaveis para Claude Code.

```bash
# Adicionar marketplace
claude plugins add BooPixel/boopixel-strategy

# Instalar skill
claude plugins install <skill-name>@BooPixel-boopixel-strategy
```

| Skill | Category | Description |
|-------|----------|-------------|
| [boopixel-db](skills/boopixel-db/SKILL.md) | database | Manipular banco de dados de producao BooPixel — projetos, charges, customers, subscriptions, plans, offerings, assets |
| [boopixel-deploy](skills/boopixel-deploy/SKILL.md) | infrastructure | Deploy business-api (AWS SAM) e business-frontend (AWS Amplify) para dev ou prod |
| [hostinger](skills/hostinger/SKILL.md) | infrastructure | Gerenciar conta Hostinger via API — websites, dominios, DNS, billing, VPS, Docker |
| [boopixel-strategy](skills/boopixel-strategy/SKILL.md) | business | Auto-documentar e manter estrategia BooPixel — pricing, clientes, planos, processos |

---

## Quick Reference

### Active Plans (7)

| Plan | Monthly | Annual | Target |
|------|---------|--------|--------|
| Essential | R$ 161,25 | R$ 1.935 | Existing clients |
| Professional | R$ 250 | R$ 2.500 | Upgrade existing |
| Complete | R$ 497 | R$ 4.970 | Upgrade existing |
| Starter | R$ 497 | R$ 4.970 | New clients |
| Growth | R$ 1.497 | R$ 14.970 | New clients |
| Scale | R$ 3.997 | R$ 39.970 | New clients |
| AI Agent | R$ 997 | R$ 9.970 | Addon (any plan) |

### Active Clients (6)

| Client | Plan | Annual | Since |
|--------|------|--------|-------|
| Caminho das Origens | Essential | R$ 2.112 | ago/2020 |
| Magsinos | Essential | R$ 2.076 | set/2019 |
| PSK Ambiental | Essential | R$ 1.935 | set/2019 |
| Pedreira Griebeler | Essential | R$ 1.935 | set/2019 |
| Preto Imoveis | Essential | R$ 1.935 | jun/2019 |
| Licenca Consultoria | A definir | R$ 0 | — |

**MRR:** ~R$ 832/mes | **ARR:** ~R$ 9.993/ano

### Infrastructure

| Resource | Provider | Cost |
|----------|----------|------|
| Cloud Startup (27 sites) | Hostinger | R$ 1.560/ano |
| Domains (.com.br x2) | Hostinger | R$ 195 cada/3 anos |
| Domain (.com x1) | Hostinger | R$ 140/ano |
| Backend API | AWS Lambda | pay-per-use |
| Frontend | AWS Amplify | pay-per-use |
| Database | MySQL (Hostinger) | incluso no hosting |
