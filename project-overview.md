# BooPixel — Visão do Projeto

Documento único que descreve o produto BooPixel: o que é, como se ganha dinheiro, quais sistemas existem, como conversam entre si e o que cada repositório entrega.

Links úteis:
- App: https://app.boopixel.com
- Strategy: https://github.com/BooPixel/boopixel-strategy
- API: https://github.com/BooPixel/business-api
- Frontend: https://github.com/BooPixel/business-frontend

---

## 1. O que é a BooPixel

Plataforma de serviços digitais para pequenas e médias empresas, combinando:

- **Criação e manutenção de sites** (landing pages, institucionais, e-commerce, sistemas web)
- **Automação com IA** (chatbots, agentes de atendimento WhatsApp/Chat, automação de processos)
- **Marketing digital e SEO**
- **Identidade visual e branding**
- **Consultoria**

Diferencial competitivo: oferecer **site + IA + automação** como pacote integrado, posicionando acima de freelancers/fábricas de site e abaixo de agências premium. Referência: [pricing.md](https://github.com/BooPixel/boopixel-strategy/blob/master/pricing.md).

---

## 2. Modelo de negócio

### Catálogo (implementado)
- **8 planos** em 3 categorias:
  - Maintenance: Essential (R$ 250/mes) · Professional (R$ 497/mes) · Advanced (R$ 797/mes)
  - Premium: Business (R$ 1.497/mes) · Growth (R$ 2.497/mes) · Enterprise (R$ 3.997/mes)
  - Addon: AI Agent (R$ 997/mes) · Automation (R$ 1.497/mes)
- **13 offerings** ativos (landing-page, site-institucional, e-commerce, agente-ia, seo-mensal, branding, automacao, webmaster, midias-sociais, backup, ssl, dominio, email-profissional)
- **3 plan_categories** (maintenance, premium, addon) com pricing page publica
- **Tipos de servico** (ServiceType) — categoria editavel
- **4 descontos** padrao: ANUAL (1 mes gratis), BUNDLE10, INDICA, TRIAL50
- **5 subscriptions** ativas (plano Essential legado) + **6 clientes** ativos
- **Yearly = 11x monthly** (desconto de 1 mes)

### Modelos de cobrança
- **Recorrente** — assinatura mensal/anual (Subscription)
- **One-time** — venda avulsa (Project com `setup_fee`)
- **Híbrido** — setup + mensalidade (Project com `setup_fee` + `recurring_price`)

### Estrutura jurídica
Sociedade LTDA entre dois sócios (50/50). Fluxo completo de abertura em [cnpj-ltda.md](https://github.com/BooPixel/boopixel-strategy/blob/master/cnpj-ltda.md).

---

## 3. Arquitetura

### Repositórios

| Repo | Papel | Stack | Status |
|---|---|---|---|
| `boopixel-strategy` | Documentação de produto, preços, templates de formulários, decisões estratégicas | Markdown + JSON | Ativo |
| `business-api` | Backend REST multi-tenant — auth, CRM, cobranças, integrações cloud, catálogo de serviços, messaging, bot IA, domínios | Python 3.13, FastAPI, SQLAlchemy, MySQL, Alembic | Ativo |
| `business-frontend` | SPA admin + cliente + pricing page pública | React, React Router, Bootstrap, i18next, Lucide, Recharts | Ativo |
| `landing-page` | Landing page BooPixel + tema WordPress com widgets Elementor | HTML/CSS/JS + PHP (WordPress theme) | Ativo |
| `help-api` | API de licenciamento BooChat Connect PRO | Python 3.12, FastAPI, MySQL | Ativo |
| `help-plugin` | Plugin WordPress — chatbot IA integrado com n8n (BooPixel AI Chat Connect) | PHP 7.2+, WordPress | Ativo |
| `ai-marketing` | Scripts de processamento de imagens para marketing (Instagram feed, carrossel) | Python, Pillow | Utilitário |
| `bp-abraccc` | Sistema de consulta pública Studbook (ABRACCC) | — | Legado |
| `cloud-api` | (reservado) | — | Inativo |
| `crm-api` | (reservado) | — | Inativo |

### Infraestrutura

- **API**: AWS Lambda (SAM) + API Gateway HTTP, empacotada via layer (`dependencies/requirements.txt`). Deploy: `make deploy-prod`.
- **Frontend**: AWS Amplify Hosting (build automático a partir de `master`). Deploy: push ou `make frontend-prod`.
- **Banco**: MySQL gerenciado (Hostinger).
- **E-mail transacional**: SMTP da Hostinger (porta 465) para invites, notificações de lead, alertas admin.
- **Cloud integrations**: Registro.br via RDAP (domínios dos clientes); Hostinger API (listagem de domínios via `DomainService`); arquitetura pronta para adicionar outros providers.

### Fluxo de autenticação

- JWT com `access_token` em memória (imune a XSS via web storage)
- `refresh_token` em `localStorage` (sobrevive fechar/abrir aba/browser)
- Rehydrate no bootstrap do app via `/auth/refresh` single-flight (evita race entre bootstrap e 401-retry)
- Contextos: `admin` (operador da empresa) e `client` (cliente final)

---

## 4. Domínio — modelo de dados

```mermaid
erDiagram
    Company ||--o{ User : "via UserCompany"
    Company ||--o{ Plan : "catálogo"
    Company ||--o{ Offering : "catálogo"
    Company ||--o{ Discount : "catálogo"
    Company ||--o{ ServiceType : "catálogo"
    Company ||--o{ AssetType : "catálogo"
    ServiceType ||--o{ Offering : "categoriza"
    ServiceType ||--o{ AssetType : "agrupa"
    Plan ||--o{ PlanItem : "inclui"
    Offering ||--o{ PlanItem : "referencia"
    User ||--o{ Subscription : "assina"
    Plan ||--o{ Subscription : "é assinado"
    User ||--o{ Project : "contrata"
    Offering ||--o{ Project : "é contratado"
    Subscription }o--|| Discount : "aplica"
    Project }o--|| Discount : "aplica"
    Project ||--o{ ServiceAsset : "possui"
    Project ||--o{ Charge : "gera"
    User ||--o{ Charge : "recebe"
    AssetType ||--o{ ServiceAsset : "tipifica"
    Company ||--o{ Lead : "captura"
    Company ||--o{ FormTemplate : "publica"
    Lead ||--o| User : "convertido em"
```

### Conceitos principais

| Entidade | Papel |
|---|---|
| **Company** | Tenant (agência). Toda linha do sistema é escopada por `company_id`. |
| **User** | Pessoa. Pode ser admin da Company ou cliente final (`customer`). Vínculo via `UserCompany` com role. |
| **Lead** | Contato capturado via formulário público. Pode ser convertido em User. |
| **FormTemplate** | Template de formulário conversacional. JSON-driven, editável no admin. Strategy: [lead-capture-forms.md](https://github.com/BooPixel/boopixel-strategy/blob/master/lead-capture-forms.md). |
| **ServiceType** | Catálogo de tipos (Sites, IA, Marketing, Branding, Automação, Consultoria, Mídias Sociais, etc.). Categoriza Offerings e AssetTypes. |
| **AssetType** | Tipo de ativo técnico (Domínio, Hosting, E-mail, Credencial, etc.). Vinculado a ServiceType. |
| **Offering** | Serviço vendável individual (Landing Page, SEO, IA Agente). Tem `service_type_id`, `pricing_model` ∈ {one_time, recurring, hybrid}, `price_from`, `setup_fee`, `recurring_price`. |
| **Plan** | Pacote (Starter/Growth/Scale) com `tier`, `price_monthly`, `price_yearly`, `trial_days`. Agrupa Offerings via PlanItem. |
| **PlanItem** | Bridge Plan × Offering. `quantity` + `limit_note` (texto livre, informativo). |
| **Discount** | Regra reutilizável. `type` ∈ {percent, fixed, months_free}, `applies_to` ∈ {plan, offering, any}, `code` opcional, `valid_from/until`, `max_uses`, `min_months`. |
| **Subscription** | Assinatura ativa: `customer_id`, `plan_id`, `discount_id`, `billing_cycle` ∈ {monthly, yearly}, `status` ∈ {trialing, active, paused, cancelled, expired}, `current_period_end` (gatilho de cobrança). |
| **Project** | Venda avulsa: `customer_id`, `offering_id`, `discount_id`, `setup_fee`, `recurring_price`, `status` ∈ {proposal, in_progress, **active**, delivered, paid, archived}. `active` = projeto contínuo (manutenção, mensal). |
| **ServiceAsset** | Ativo técnico de um Project (domínio, hosting, credenciais cifradas). Action `lookup` consulta dados live (Registro.br RDAP) e sincroniza `expires_at`. |
| **Charge** | Cobrança individual. Pode estar vinculada a um Project (`project_id`). |
| **Transaction** | Movimentação financeira (entrada/saída). |
| **CustomerEmail** | E-mails adicionais do cliente para notificação. |
| **Message** | Mensagem de qualquer canal (WhatsApp, Telegram, etc.). `channel`, `direction` ∈ {inbound, outbound}, `status`, `is_read`, `external_id`. |
| **MessageContact** | Contato com display_name editável + flag `bot_paused`. Unique por (company, channel, identifier). Auto-seed do perfil WhatsApp. |
| **Configuration** | Key-value genérico por empresa. JSON serializado. Usado pra bot settings (`key=bot`). |

---

## 5. Fluxos principais

### 5.1 Signup
Cadastro cria **User + Company** em uma operação. Convites linkam novos usuários a uma Company existente. Detalhes em [financial-system.md](https://github.com/BooPixel/boopixel-strategy/blob/master/financial-system.md).

### 5.2 Captação de lead
1. Visitante acessa `app.boopixel.com/form/<slug>`
2. Preenche o chat wizard (steps definidos em `FormTemplate` JSON)
3. `POST /api/v1/public/leads/<company_slug>` cria `Lead`
4. Admin recebe e-mail de notificação
5. Admin converte Lead → User (customer)

### 5.3 Configuração inicial do catálogo
1. Admin cadastra `ServiceType` (categorias: Sites, IA, Marketing…) em `/catalog/service-types`
2. Admin cadastra `Offering` em `/catalog/services` (slug, nome, tipo de serviço, modelo de cobrança, preço a partir de…)
3. Admin monta `Plan` em `/catalog/plans` agrupando Offerings via PlanItem
4. Admin cria `Discount` reutilizável em `/catalog/discounts`

### 5.4 Venda
- **Pacote (Starter/Growth/Scale)** → cria `Subscription(customer, plan, billing_cycle)` em `/sales/subscriptions/new`
- **Avulso** → cria `Project(customer, offering, setup_fee)` em `/sales/projects/new`
- **Híbrido** → `Project` com `setup_fee` + `recurring_price`
- **Contínuo** → `Project` com `status=active` (manutenção, sem entrega final)
- Desconto aplicado via `discount_id`

### 5.5 Cobrança recorrente (a implementar)
Hoje: cobrança gerada manualmente via `/charges/new`.
Próximo passo: job periódico lê `Subscription.current_period_end` e gera `Charge` automaticamente.

### 5.6 Gestão de ativos (cloud integrations)
- Cada `ServiceAsset` pode apontar pra um provider (`registro.br`, futuros)
- Action `lookup` genérica consulta dados live (status, expiração, nameservers) via RDAP
- Sincronização automática de `expires_at` quando divergir do registrador
- UI: `/sales/projects/:id` → expand do asset → menu 3-pontos → "Verificar domínio"

---

## 6. Estrutura de pastas (API)

```
business-api/
├── app/
│   ├── abc/                  # Abstract Base Classes
│   │   ├── bot.py            # Bot interface
│   │   ├── email.py          # EmailSender, TemplateLoader
│   │   ├── llm_provider.py   # LLMProvider ABC, ConversationTurn, AgentConfig
│   │   └── message.py        # IncomingMessage, OutgoingMessage, MessageProvider, SendResult
│   ├── api/v1/routers/       # endpoints REST (auth, charges, messages, whatsapp, bot-settings, domains, company, invites)
│   ├── integrations/
│   │   ├── channels/         # WhatsApp provider (implementa MessageProvider ABC)
│   │   ├── cloud/            # Registro.br RDAP + base cloud provider
│   │   ├── email/            # SMTP sender, templates, service
│   │   └── llm/              # Multi-provider LLM factory (Gemini, OpenAI, Anthropic)
│   ├── core/                 # auth, security, settings, listing (paginação)
│   ├── db/                   # base, mixins, tipos
│   ├── models/               # SQLAlchemy (20+ modelos)
│   ├── repositories/         # acesso a dados
│   ├── schemas/              # Pydantic (request/response)
│   └── services/
│       ├── channels/         # BotEngine (LLM-backed, handoff, per-contact pause)
│       ├── asset_actions/    # ações genéricas por asset (registry pattern)
│       └── ...               # lead, charge, message, bot_settings, etc.
├── alembic/                  # migrations
├── template.yaml             # AWS SAM (Lambda + API Gateway + env vars declarativas)
├── dependencies/             # requirements.txt (Lambda layer)
└── requirements-lambda.txt  # idem
```

## 7. Estrutura de pastas (Frontend)

```
business-frontend/
├── src/
│   ├── api/                 # axios config, endpoints, services
│   ├── components/          # atoms / molecules / templates
│   ├── contexts/            # AuthContext, ThemeContext, NotificationsContext
│   ├── guards/              # ProtectedRoute, RoleProtectedRoute
│   ├── hooks/               # useRequest, useAuth, use<Entity>
│   ├── i18n/                # pt / en (sincronizados)
│   └── pages/
│       ├── admin/
│       │   ├── catalog/     # services, plans, discounts, service-types, asset-types
│       │   ├── sales/       # subscriptions, projects + ProjectDetail
│       │   ├── customers/   # CRM
│       │   ├── charges/     # cobranças
│       │   ├── transactions/# financeiro
│       │   ├── leads/       # leads capturados
│       │   ├── messages/    # chat estilo WhatsApp + envio
│       │   ├── bot/         # configuração do bot IA (prompt, modelo, toggle)
│       │   ├── contracts/   # contratos (scaffold, dados mock)
│       │   ├── products/    # produtos (scaffold, dados mock)
│       │   ├── company/     # configurações da empresa
│       │   ├── dashboard/   # métricas + gráficos (Recharts)
│       │   ├── invites/     # convites de usuário
│       │   ├── profile/     # perfil do admin
│       │   ├── settings/    # configurações gerais
│       │   ├── payments/    # pagamentos
│       │   └── formTemplates/
│       └── client/          # área do cliente final
```

### Sidebar (estrutura atual)

- **Operations**: Início (Dashboard) · Cobranças · Transações
- **Contacts**: Clientes · Leads · Canais (submenu: Mensagens + Prompt IA) · Formulários · Convites
- **Catalog**: Serviços (submenu: Tipos de Serviço, Tipos de Ativo) · Planos (submenu: Categorias) · Descontos
- **Sales**: Assinaturas · Projetos · Contratos (mock) · Produtos (mock)
- Footer: Configurações · Perfil · Empresa

### Header

- Sino de notificações com badge de não lidas (polling 10s)
- Tab title flash com emoji  quando nova mensagem com aba oculta
- Notificação nativa do SO (browser Notification API)

---

## 8. Decisões de produto já tomadas

- Multi-tenant por `company_id` em todas as tabelas
- Catálogo (Plan/Offering/Discount/ServiceType/AssetType) **por company**, não global
- Limites de plano informativos (texto livre em `PlanItem.limit_note`), não duros
- Preço via "faixa mínima" (`Offering.price_from`), valor real negociado no `Project`
- Modelo de venda híbrido: `Subscription` (recorrente) + `Project` (one-time/híbrido/contínuo)
- Status `active` em `Project` = projeto contínuo (manutenção mensal)
- `Offering.service_type_id` (FK) substitui enum `category` hardcoded — categorias agora editáveis
- Credenciais de asset cifradas simetricamente antes de persistir
- Actions de asset via registry genérico (add nova action = novo arquivo)
- Service legacy completamente removido (migrado pra Project + Offering)
- Paginação padrão (`PaginatedResponse[T]`) em todos os endpoints de listagem
- ABCs extraídos em `app/abc/` — contratos separados de implementações
- LLM multi-provider via factory (`get_provider(model)`) — Gemini, OpenAI, Anthropic
- Integrações isoladas em `app/integrations/` (channels, cloud, email, llm)
- Bot LLM-only (sem fallback keyword) com handoff sentinel `[[HANDOFF]]`
- Configurações genéricas via tabela `configurations` (key-value JSON por empresa)
- Contatos com `bot_paused` — admin pode pausar/resumir bot por contato
- `customer_emails` renomeado pra `user_emails`

---

## 9. Status de implementação

### Pronto
- Catálogo completo: ServiceType, AssetType, Offering, Plan, PlanItem, Discount
- Vendas: Subscription + Project (com status `active` pra contínuo)
- Páginas admin (lista + form com seções em cards + detail) pra todas as entidades
- Migração de Service legacy → Project (34 services migrados, 14 assets + 235 charges relinkados)
- Drop completo do Service model + tabela
- Cloud integration Registro.br (RDAP) com action `lookup` genérica
- Auth com bootstrap rehydrate (refresh token sobrevive fechar/abrir aba)
- Paginação padrão
- Toggle/badge styling, currency formatting (R$ 1.500,00) em todas as listas
- **PlanCategory** — tabela + CRUD admin + seed (maintenance, premium, addon)
- **Pricing page pública** — `/pricing` e `/planos`, dinâmica, toggle mensal/anual, SEO completo (OG, JSON-LD, sitemap.xml, robots.txt)
- **Lead modal na pricing** — form dinâmico vinculado ao plano via `lead_form_id`, submete lead com `plan_id` e `source`
- **Lead notification por email** — equipe notificada via SMTP (BackgroundTasks) quando chega lead novo
- **Form builder visual** — admin pode criar/editar form templates com step builder (JSON-based)
- **GA4 + Consent Mode v2** — Google Analytics (G-XFS7Y4F884) com cookie banner e consent management
- **Home → Pricing** — service cards na home linkam direto pra `/pricing`
- **Performance** — eager-load de relações (fix N+1), memoize pricing computations, throttled scroll, inline asset actions
- **Client portal** — `/client/payments` para clientes verem suas cobranças
- **CustomerEmail** — emails adicionais de notificação por cliente
- **Dashboard** — métricas de transações com gráficos (Recharts), date range picker, year-over-year
- **WhatsApp Cloud API** — webhook + bot auto-reply + persistência de mensagens no banco
- **Messaging genérico** — arquitetura multi-canal (WhatsApp/Telegram/Discord) com providers ABC
- **Privacy/Terms estáticos** — páginas HTML estáticas pra verificação Meta
- **Chat UI estilo WhatsApp** — painel contatos + thread com bolhas, envio pelo admin, responsivo mobile
- **Envio de mensagens pelo admin** — `POST /messages/send`, textarea com Enter pra enviar
- **Contatos editáveis** — tabela `message_contacts` com display_name custom, auto-seed do perfil WhatsApp
- **Unread tracking** — coluna `is_read`, endpoint `/messages/unread`, mark-read por conversa
- **Notificações** — sino no header com badge, polling 10s, tab title flash, notificação nativa do SO
- **Bot IA com Gemini** — `GeminiAgent` (gemini-2.5-flash), histórico de conversa, system prompt configurável
- **Bot settings** — página `/bot` pra editar prompt, modelo e toggle on/off, persistido na tabela `configurations`
- **Tabela genérica `configurations`** — key-value JSON por empresa (substitui bot_settings)
- **SAM template declarativo** — env vars Gemini + WhatsApp gerenciadas via CloudFormation
- **Handoff humano** — `[[HANDOFF]]` no output do LLM pausa bot pra contato, flag `bot_paused` em `message_contacts`
- **Domain service** — listagem de domínios da empresa via Hostinger API com dados live (`GET /domains`)
- **Invite expiry fix** — comparação de datetime com valores naive do banco corrigida
- **Migration tooling** — ferramentas de migração adicionadas ao projeto API
- **Message contacts enriquecidos** — last_message e unread_count no endpoint de contatos
- **Lucide icons** — emojis substituídos por SVGs do Lucide em todo o chat UI
- **Polling otimizado** — intervalos de polling reduzidos pra aliviar limite de conexões do banco
- **Google Console layout** — admin shell redesenhado no estilo Google Console
- **Scaffold contracts/products** — páginas frontend com dados mock (sem backend ainda)

### Roadmap

#### Fase 1 — Automatizar cobranca (urgente)

> 5 subscriptions ativas, 0 charges recorrentes. Sub #3 (PSK Ambiental) ja venceu em mar/2026. SMTP configurado e funcional. Lead notification ja funciona via BackgroundTasks.

- [ ] Geracao automatica de `Charge` a partir de `Subscription.current_period_end`
- [ ] Cron job (EventBridge → Lambda) pra cobranca recorrente
- [ ] Notificacao por e-mail antes da cobranca vencer

#### Fase 2 — Formalizar operacao

> Depende do CNPJ abrir pra faturas. Discounts existem no banco (4) mas sem logica no backend.

- [ ] Calculo efetivo de desconto aplicado (percent/fixed/months_free)
- [ ] Invoices/faturas e recibos em PDF (apos CNPJ abrir)
- [ ] Upgrade/downgrade de Subscription preservando historico

#### Fase 3 — Escalar

> So faz sentido com novos clientes. Clientes atuais pagam via transferencia.

- [ ] Integracao Stripe (cobranca cartao)
- [ ] Seed automatico do catalogo BooPixel (script idempotente pra dev/test)
- [ ] Meta Pixel + Conversions API (Facebook/Instagram tracking)
- [ ] Dashboard de leads (funil visual, leads por source, SLA)
- [ ] Lead capture via conversa WhatsApp
- [ ] Template messages aprovadas pelo Meta
- [ ] Tool use Gemini (create_lead, get_pricing, schedule_handoff)
- [ ] Grounding RAG com docs de serviços/preços
- [ ] Status real outbound (delivered/read via webhook statuses[])
- [ ] Tela genérica de Configurations (CRUD qualquer key)

#### Removidos/adiados

- ~~Migrar `refresh_token` para cookie `httpOnly`~~ — nice-to-have, sem impacto no negocio
- ~~Adicionar mais cloud providers (Cloudflare, Route53)~~ — tudo na Hostinger, sem necessidade real
- ~~Configurar GA4 e GTM~~ — **FEITO** (G-XFS7Y4F884 com Consent Mode v2)
- ~~Pricing page publica~~ — **FEITO** (/pricing e /planos com SEO, modal de lead, categorias)
- ~~Notificacao email para leads~~ — **FEITO** (BackgroundTasks + SMTP Hostinger)
- ~~Form builder visual no admin~~ — **FEITO** (StepsBuilder com JSON step editor)
- ~~WhatsApp Cloud API~~ — **FEITO** (webhook + bot IA Gemini + chat UI + notificações + contatos editáveis)
- ~~Publicar app Meta~~ — **FEITO** (app Live, webhook verificado, WABA subscribed)
- ~~Bot auto-reply~~ — **FEITO** (evoluiu pra Gemini LLM com histórico + handoff humano)
- ~~Dashboard de mensagens~~ — **FEITO** (chat estilo WhatsApp com envio, contatos, unread tracking)
- ~~Notificações~~ — **FEITO** (sino, polling 10s, tab flash, notificação nativa SO)

---

## 10. Referências

- [Financial System](https://github.com/BooPixel/boopixel-strategy/blob/master/financial-system.md) — modelagem de dados, fluxo de signup, regras de negócio
- [Lead Capture Forms](https://github.com/BooPixel/boopixel-strategy/blob/master/lead-capture-forms.md) — estratégia conversacional, personas, pipeline
- [Pricing](https://github.com/BooPixel/boopixel-strategy/blob/master/pricing.md) — preços, margens, comparativo
- [CNPJ LTDA](https://github.com/BooPixel/boopixel-strategy/blob/master/cnpj-ltda.md) — abertura jurídica
- [CLAUDE.md](https://github.com/BooPixel/business-api/blob/master/CLAUDE.md) — regras do projeto business-api para o Claude
- [Database Options](https://github.com/BooPixel/boopixel-strategy/blob/master/database-options.md) — comparação de MySQL hosting
