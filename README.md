# BooPixel Strategy

Strategic documentation, system modeling and skills for **BooPixel** — https://app.boopixel.com/

---

## Documents

| Document | Category | Description |
|----------|----------|-------------|
| [Pricing](pricing.md) | Business | Plans, offerings, margins, market reference, active clients |
| [CNPJ LTDA](cnpj-ltda.md) | Business | Abertura de CNPJ LTDA — checklist, custos, contabilidade, fluxo |
| [Project Overview](project-overview.md) | Business | Visao geral do projeto BooPixel |
| [Financial System](financial-system.md) | Product | Data modeling, signup flow, business rules, multi-tenant financial system |
| [Lead Capture Forms](lead-capture-forms.md) | Product | Form strategy, personas, copy patterns, pipeline, roadmap ([`forms/`](forms/)) |
| [Pricing Page](pricing-page.md) | Product | Arquitetura da /pricing publica — modelo de dados, endpoints, admin, fluxo |
| [Google Ads](google-ads.md) | Marketing | Estrategia de anuncios Google Ads — campanhas, keywords, budget, metricas |
| [Meta Ads](meta-ads.md) | Marketing | Estrategia Facebook + Instagram — campanhas, criativos, segmentacao, Advantage+ |
| [WhatsApp API](whatsapp-api.md) | Integration | WhatsApp Cloud API — configuração, webhook, templates, bot strategy |
| [Database Options](database-options.md) | Infrastructure | Comparação de opções MySQL hosting (EC2, Lightsail, RDS, PlanetScale, Hostinger) |
| [Scripts](scripts/) | Tools | Scripts Python — gerador de criativos (Pillow) + publisher Meta Ads |

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

