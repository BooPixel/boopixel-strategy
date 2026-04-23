# BooPixel — Estratégia de Captação & Formulários

> Playbook de lead generation via formulário conversacional, personas, copy patterns, pipeline de leads e roadmap.
>
> Os JSONs em [`forms/`](forms/) são a fonte de verdade dos templates que vão pra tabela `form_templates` do CRM.

---

## Sumário

1. [Visão geral](#1-visão-geral)
2. [Formulários implementados](#2-formulários-implementados)
3. [Personas e jornadas](#3-personas-e-jornadas)
4. [Ideias de formulários por campanha](#4-ideias-de-formulários-por-campanha)
5. [Copy patterns do chatbot](#5-copy-patterns-do-chatbot)
6. [Pipeline de leads](#6-pipeline-de-leads)
7. [Integrações futuras](#7-integrações-futuras)
8. [Métricas e funil](#8-métricas-e-funil)
9. [Roadmap](#9-roadmap)
10. [Schema de formulário (referência)](#10-schema-de-formulário-referência)

---

## 1. Visão geral

A BooPixel captura leads via **formulário conversacional** (chat wizard) em vez de form estático tradicional. Premissas:

- **Conversa > formulário** — cliente responde ao longo do chat, percebe menos atrito que um form de 7 campos de cabeça.
- **Qualificação embutida** — a própria conversa filtra leads (orçamento, tipo de projeto, tipo de demanda) antes de chegar na equipe comercial.
- **Ancoragem de preço** — o bot menciona faixa de investimento antes de pedir info final, pra descartar leads fora do perfil e validar expectativa de quem está dentro.
- **Templates por contexto** — diferentes landings/campanhas podem ter flows diferentes (ex: campanha de evento pontual ≠ captação de site institucional).

O backend (`business-api`) tem endpoints:
- `POST /api/v1/public/leads/:company_slug` — submit do form
- `GET /api/v1/public/forms/:company_slug` — default form da empresa
- `GET /api/v1/public/forms/:company_slug/:form_slug` — form específico

O frontend (`business-frontend`) renderiza em `/form/:slug` e admin gerencia em `/forms`.

---

## 2. Formulários implementados

### 2.1 Formulário padrão BooPixel (`default`)

**Slug público:** `/form/boopixel`

**Steps:** 10+ (name → email → phone → demand → [company] → project → [current_url] → need → estimate (auto) → budget → extra → done)

**Ramificações:**
- `demand=Empresarial` → pergunta nome da empresa (`company`)
- `demand=Pessoal` → pula direto pra `project`
- `project=Alterar site | Novo site` → pede URL atual (`current_url`)
- `project=Primeiro site | Sistema/App/Plataforma` → pula pra `need`

**Faixas de preço apresentadas:**
- R$ 5.500 — soluções customizadas básicas
- R$ 11.000 — e-commerce / integrações avançadas
- Parcela em boleto

### 2.2 [`landing-evento`](forms/landing-evento.json)

Flow curto (9 steps) pra produtores de evento com data, escopo e faixa R$ 1.500–5.500.

### 2.3 [`sistema-mvp`](forms/sistema-mvp.json)

Flow qualificado (12 steps) pra demandas técnicas: estágio, volume de usuários, integrações. Faixa R$ 15k–60k.

### 2.4 [`revisao-site`](forms/revisao-site.json)

Flow para clientes com site existente querendo SEO/redesign/performance. Inclui URL atual + oferta de auditoria gratuita.

---

## 3. Personas e jornadas

| Persona | Momento | Objetivo | Ponto de dor |
|---------|---------|----------|--------------|
| **Empresário pequeno/médio** (PJ) | Quer profissionalizar presença digital | Site institucional rápido | Já tentou "fazer no Wix" e abandonou, precisa de alguém cuidando |
| **Empresa em expansão** | E-commerce ou automação | Integração com ERP/CRM, múltiplas páginas | Time interno pequeno, precisa parceiro técnico |
| **Evento/campanha pontual** (PJ) | Landing de curto prazo | Site de evento, landing de lançamento | Prazo apertado, budget limitado |
| **Pessoa física profissional** | Portfolio/consultório | Site simples com agendamento | Não é técnico, quer parcelar |
| **Pessoa física startup** | MVP de app/sistema | Validação rápida | Sem time técnico, precisa MVP enxuto |

Cada persona → um fluxo diferente com perguntas específicas, copy adequado e faixa de preço calibrada.

---

## 4. Ideias de formulários por campanha

### 4.1 `site-empresarial` — Site institucional PJ

**Público:** empresas que chegam via Google orgânico "site empresarial profissional"

**Diferenças do default:**
- Pula pergunta de "pessoal ou empresarial" (já assume PJ)
- Pergunta **segmento** (e-commerce / serviços / indústria / saúde / outro) pra roteamento interno
- Faixa de preço centrada em R$ 5.500–11.000
- Pergunta se tem **prazo** (até 30d / 60d / 90d / sem pressa)

### 4.2 `landing-evento` — Landing para evento pontual (implementado)

Já implementado — ver [`forms/landing-evento.json`](forms/landing-evento.json).

### 4.3 `sistema-mvp` — Sistema/app/plataforma (implementado)

Já implementado — ver [`forms/sistema-mvp.json`](forms/sistema-mvp.json).

### 4.4 `revisao-site` — Manutenção/melhoria (implementado)

Já implementado — ver [`forms/revisao-site.json`](forms/revisao-site.json).

### 4.5 `indicacao` — Lead por indicação

**Público:** prospects vindos de cliente atual

**Diferenças:**
- Pergunta **quem indicou** no início — vai pro source + notes
- Copy mais direto: "X te recomendou, queremos entender seu projeto"
- Prioridade de atendimento alta (SLA menor)

### 4.6 `whatsapp-bot` — Chatbot no WhatsApp

**Estratégia:** mesmo flow, mas em WhatsApp Business API em vez de site

**Ideia:** reutilizar o mesmo JSON de steps, só muda o renderizador. Webhook no backend recebe mensagens e responde seguindo o schema.

---

## 5. Copy patterns do chatbot

Padrões de linguagem que funcionam bem:

### 5.1 Saudação que agradece
> "Olá! Obrigado por considerar a BooPixel para seu projeto..."

**Por quê:** reconhecimento prévio reduz defesa, cliente já se comprometeu a preencher.

### 5.2 Justificativa antes de pedir dado sensível
> "Preciso do seu e-mail **para nossa equipe analisar seu projeto e criar a melhor solução**."
> "Qual é o seu telefone? **Assim, podemos ligar caso surja alguma dúvida sobre o seu orçamento.**"

**Por quê:** cliente entende o porquê, resistência cai. Nunca peça dado sem justificar.

### 5.3 Validação amigável
> "Esse e-mail nao parece correto, vamos tentar novamente."

**Por quê:** tom acolhedor em vez de "ERRO: email inválido".

### 5.4 Ancoragem de preço dupla
> "Para soluções customizadas: a partir de R$ 5.500.
> Projetos com e-commerce/integrações: a partir de R$ 11.000.
> **Vale lembrar que pode ser parcelado no boleto.**"

**Por quê:** cliente se posiciona em uma das faixas, filtra quem está fora do perfil **antes** de continuar.

### 5.5 Reconhecimento final + expectativa de retorno
> "Já encaminhei seus dados para nossa equipe. Você receberá nosso contato em breve por email ou telefone."

**Por quê:** fecha com sensação de ação tomada, não "aguarde silenciosamente".

### 5.6 Evitar
- Linguagem corporativa ("prezado", "atenciosamente")
- Perguntas sem contexto ("Qual seu faturamento?" sem justificativa)
- Confirmações excessivas ("Confirma seu email?") — só valida uma vez
- Mais de 12 steps — cansa. Ideal: 6-10.

---

## 6. Pipeline de leads

Status usado na tabela `leads`:

| Status | Quando | Ação comercial |
|--------|--------|----------------|
| `new` | Recém-chegado do form | Contatar em até 24h (SLA depende da campanha) |
| `contacted` | Primeiro contato feito | Agendar reunião ou enviar proposta |
| `qualified` | Tem fit, budget e timing | Proposta formal enviada |
| `converted` | Virou cliente | Cria `User` + `UserCompany` link |
| `lost` | Fora de perfil ou desistiu | Motivo no `notes` |

### 6.1 Fontes (`source`)

Toda submissão carrega um `source` via `?source=x` na URL:

- `organic-search`
- `google-ads-site`
- `google-ads-ecommerce`
- `facebook-ads`
- `indicacao-cliente-{nome}`
- `evento-{nome}`
- `linkedin`
- `direct`
- `chat` (fallback default)

Permite filtrar no dashboard admin e calcular ROI por canal.

### 6.2 SLA por origem

| Source | Primeiro contato |
|--------|------------------|
| `indicacao-*` | 2h (prioridade alta) |
| `google-ads-*` | 12h (lead quente, pagamos pelo clique) |
| `organic-search` | 24h |
| `linkedin` | 48h |
| Outros | 72h |

---

## 7. Integrações futuras

### 7.1 Notificação por email

**Status: IMPLEMENTADO** 

Quando chega lead novo: email pro time comercial (endereços em `LEAD_NOTIFICATION_EMAILS` comma-separated). Conteúdo: nome, email, telefone, fonte, resumo das respostas. Implementado via `BackgroundTasks` no `lead_service._notify_team()`. Template `new_lead` (pt-BR) via SMTP Hostinger.

### 7.2 Integração com CRM externo

**Prioridade: média**

Conectores pra:
- **RD Station** / **HubSpot** — sync de leads via API
- **Pipedrive** — pipeline comercial espelhado

### 7.3 Email marketing pós-lead

**Prioridade: média**

Quando lead entra → dispara fluxo de nutrição de 5 emails em 14 dias:
1. Dia 0 — Obrigado + case study
2. Dia 2 — Depoimento de cliente no mesmo segmento
3. Dia 5 — Guia técnico (lead magnet)
4. Dia 9 — Convite pra agendar conversa
5. Dia 14 — Última oportunidade / desconto first-time

Ferramenta candidata: **Mailerlite** (barato, API boa) ou **ActiveCampaign** (mais pesado, trigger por evento).

### 7.4 WhatsApp Business API

**Status: IMPLEMENTADO (parcial)** 

Webhook + bot auto-reply funcionando em produção. Detalhes em [whatsapp-api.md](whatsapp-api.md).

-  Webhook recebe mensagens em tempo real
-  Bot responde automaticamente com intent detection (saudação, serviços, preços, handoff)
-  Mensagens persistidas no banco (tabela `messages`)
-  Arquitetura multi-canal (WhatsApp/Telegram/Discord via providers)
-  Lead capture via conversa (próximo passo)
-  Template messages (precisam aprovação Meta)
-  Reutilizar form JSON steps no WhatsApp

### 7.5 Calendly/agendamento

**Prioridade: média**

Pra leads qualificados, oferecer agendamento direto de call:
- Após `status=qualified`, envia link Calendly
- Integração reversa: webhook do Calendly atualiza `notes` do lead

---

## 8. Métricas e funil

### 8.1 Funil esperado

| Etapa | Taxa típica | Observação |
|-------|-------------|------------|
| Visita à landing | 100% | base de cálculo |
| Começa o form (step 1) | 10-15% | CTA bom eleva |
| Chega na pergunta de preço | 40-60% dos iniciados | abandono maior aqui |
| Termina o form | 70-85% dos que passam do preço | conversão relativa |
| Vira `contacted` | 90%+ | depende do SLA |
| Vira `qualified` | 30-50% dos contatados | filtro comercial |
| Vira `converted` | 15-25% dos qualificados | depende da proposta |

### 8.2 Sinais de alerta

- Abandono >70% no step de telefone → pedir com menos fricção (ou adiar pro final)
- Abandono >50% após ancoragem de preço → nicho/público errado pra landing
- Taxa `lost` > 50% por "fora de budget" → landing mal segmentada (traz lead barato demais)

### 8.3 Dashboard previsto

Adicionar ao `/dashboard` admin:
- Cards: leads novos (hoje / semana / mês)
- Funil visual (new → contacted → qualified → converted)
- Leads por source
- Tempo médio `new → contacted` (SLA)

---

## 9. Roadmap

### 9.1 Curto prazo (próximas 2 sprints)

- [x] Templates `landing-evento`, `sistema-mvp`, `revisao-site`
- [x] Notificação por email pro time comercial quando chega `lead.new` — `lead_service._notify_team()` via BackgroundTasks
- [x] Builder visual de forms no admin — StepsBuilder com JSON step editor, validações, branching
- [x] Modal de lead na pricing page — form dinâmico vinculado ao plano via `lead_form_id`
- [ ] Email transacional pro lead confirmando recebimento
- [ ] Página pública `/obrigado?lead={id}` com próximos passos

### 9.2 Médio prazo (1–3 meses)

- [ ] A/B testing de flows (mesma URL, 2 versões)
- [x] Integração WhatsApp Business — webhook + bot auto-reply implementado ([whatsapp-api.md](whatsapp-api.md))
- [ ] Email nurturing automatizado (integração Mailerlite)

### 9.3 Longo prazo (3+ meses)

- [ ] Score de lead (qualificação automática baseada em respostas)
- [ ] Roteamento automático por segmento (B2B ecommerce vai pro vendedor X)
- [ ] Integração com Pipedrive/RD
- [ ] Analytics dedicado com funil configurável

---

## 10. Schema de formulário (referência)

Todo form na tabela `form_templates` segue este schema JSON:

```jsonc
{
  "initial_step": "name",
  "redirect_url": "/",
  "redirect_after_seconds": 5,
  "steps": {
    "step_id": {
      "bot": ["Texto com {placeholder} e **negrito**"],
      "bot_dynamic": {
        "condition_field": "demand",
        "variants": { "Empresarial": ["Variante A"], "Pessoal": ["Variante B"] },
        "default": ["Fallback"]
      },
      "input": { "type": "text|email|tel|textarea", "placeholder": "...", "optional": false },
      "transform": "digits_only",
      "validation": {
        "type": "min_length|email|phone",
        "error": "Mensagem amigável",
        "min": 2,
        "min_digits": 10,
        "max_digits": 15
      },
      "choices": [
        { "label": "...", "subtitle": "...", "value": "stored_value", "next": "next_step_id" }
      ],
      "auto": true,
      "next": "next_step_id",
      "terminal": true
    }
  }
}
```

**Campos especiais:**
- `{name}`, `{email}`, `{company}` etc. nos textos são substituídos pelas respostas anteriores
- `**texto**` vira negrito ao renderizar
- `\n` quebra linha dentro de uma mensagem do bot
- `bot_dynamic` escolhe o array de textos baseado numa resposta anterior

---

## Links úteis

- **CRM admin:** https://app.boopixel.com/forms
- **Form default público:** https://app.boopixel.com/form/boopixel
- **Repo backend:** https://github.com/BooPixel/business-api
- **Repo frontend:** https://github.com/BooPixel/business-frontend
