# WhatsApp Business API — BooPixel

Configuração e integração da WhatsApp Cloud API para atendimento automatizado e captação de leads.

---

## Contas e Acessos

| Campo | Valor |
|-------|-------|
| Meta App ID | 945825354522145 |
| Business ID | 2100949430186290 |
| WABA ID | 2693966874336487 |
| Phone Number ID | 1011433038730788 |
| Número | +55 48 8813-5243 |
| PIN 2FA | 482613 |
| Nome exibição | BooPoixel |

### Credenciais (em ~/.env)

| Variável | Descrição |
|----------|-----------|
| `WHATSAPP_TOKEN` | Access token (expirado — gerar permanente via System User) |
| `WHATSAPP_PHONE_NUMBER_ID` | Phone Number ID (1011433038730788) |
| `WHATSAPP_WABA_ID` | WhatsApp Business Account ID (2693966874336487) |
| `WHATSAPP_APP_ID` | Meta App ID (945825354522145) |
| `WHATSAPP_BUSINESS_ID` | Business Manager ID (2100949430186290) |
| `WHATSAPP_VERIFY_TOKEN` | Webhook verification token (boopixel_webhook_2026) |
| `WHATSAPP_PIN` | PIN de verificação em duas etapas |

---

## Status Atual

| Item | Status |
|------|--------|
| App Meta criado | ✅ |
| Permissões configuradas | ✅ whatsapp_business_management, whatsapp_business_messaging |
| Número registrado | ⚠️ Em progresso (PIN definido, aguardando verificação) |
| Token permanente | ❌ Gerar via System User |
| Webhook configurado | ❌ |
| Template messages | ❌ |
| Bot/automação | ❌ |

---

## Como Gerar Token Permanente

1. Acessar: business.facebook.com/settings/system-users/?business_id=2100949430186290
2. **Add** → nome `BooPixel API` → role **Admin** → Create System User
3. No user criado → **Generate New Token**
4. Selecionar app **945825354522145**
5. Marcar permissões:
   - ✅ `whatsapp_business_management`
   - ✅ `whatsapp_business_messaging`
6. **Generate Token** → copiar (não aparece de novo!)
7. Voltar em System Users → **Add Assets** → Apps → selecionar app → **Full Control** → Save
8. Atualizar `WHATSAPP_TOKEN` no `~/.env`

> Token permanente **nunca expira** a menos que seja revogado manualmente.

---

## Webhook

### Configuração no Meta

1. Na página do app → WhatsApp → Configuration → Webhooks
2. **Callback URL:** `https://api.boopixel.com/api/v1/webhook/whatsapp` (a implementar)
3. **Verify Token:** `boopixel_webhook_2026`
4. Assinar campos: `messages`, `message_deliveries`, `message_reads`

### Implementação necessária (business-api)

```
POST /api/v1/webhook/whatsapp
├── GET  → Verificação do webhook (challenge)
├── POST → Receber mensagens e status updates
└── Handler → Parse payload → responder ou criar lead
```

### Payload de mensagem recebida

```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "2693966874336487",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {
          "display_phone_number": "5548881355243",
          "phone_number_id": "1011433038730788"
        },
        "messages": [{
          "from": "5548999999999",
          "id": "wamid.xxx",
          "timestamp": "1682000000",
          "type": "text",
          "text": { "body": "Olá, quero saber sobre os planos" }
        }]
      }
    }]
  }]
}
```

---

## Enviar Mensagem (API)

### Template message (iniciar conversa)

```bash
curl -X POST "https://graph.facebook.com/v21.0/1011433038730788/messages" \
  -H "Authorization: Bearer $WHATSAPP_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "5548999999999",
    "type": "template",
    "template": {
      "name": "hello_world",
      "language": { "code": "en_US" }
    }
  }'
```

### Mensagem de texto (dentro da janela de 24h)

```bash
curl -X POST "https://graph.facebook.com/v21.0/1011433038730788/messages" \
  -H "Authorization: Bearer $WHATSAPP_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "5548999999999",
    "type": "text",
    "text": { "body": "Olá! Obrigado pelo interesse na BooPixel." }
  }'
```

---

## Custos

### Preço por conversa (Brasil, 2026)

| Categoria | Preço/conversa |
|-----------|---------------|
| Marketing | ~$0.0625 |
| Utility | ~$0.0350 |
| Authentication | ~$0.0315 |
| Service (cliente inicia) | Grátis (primeiras 1.000/mês) |

> Primeiras 1.000 conversas de serviço por mês são gratuitas.

---

## Estratégia de Uso

### Fase 1 — Notificação de leads (curto prazo)
- Quando chega lead novo via pricing page → enviar template de boas-vindas via WhatsApp
- Admin recebe notificação no WhatsApp sobre novo lead
- Resposta manual via Meta Business Suite Inbox

### Fase 2 — Bot conversacional (médio prazo)
- Reutilizar JSON de form templates (mesmos steps do chat web)
- Webhook recebe mensagem → identifica step → responde com próxima pergunta
- Respostas por botão (mesmos `choices` do form JSON)
- Lead criado automaticamente ao final do flow

### Fase 3 — Agente IA (longo prazo)
- Integrar agente IA treinado com dados da BooPixel
- Atendimento 24/7 automático
- Handoff para humano quando necessário
- Produto vendável: addon AI Agent (R$ 997/mês)

---

## Template Messages (a criar)

Templates precisam de aprovação do Meta antes de usar.

| Nome | Categoria | Conteúdo |
|------|-----------|----------|
| `lead_welcome` | Marketing | "Olá {{1}}! Obrigado pelo interesse na BooPixel. Vamos analisar seu projeto e entrar em contato em breve." |
| `new_lead_admin` | Utility | "Novo lead: {{1}} ({{2}}). Plano: {{3}}. Fonte: {{4}}." |
| `payment_reminder` | Utility | "Olá {{1}}, sua fatura de R$ {{2}} vence em {{3}}. Qualquer dúvida, responda aqui." |
| `appointment_confirm` | Utility | "Reunião confirmada para {{1}} às {{2}}. Link: {{3}}" |

---

## Links Úteis

| Recurso | URL |
|---------|-----|
| WhatsApp Dev Console | developers.facebook.com/apps/945825354522145/whatsapp-business/wa-dev-console |
| Business Settings | business.facebook.com/settings/?business_id=2100949430186290 |
| System Users | business.facebook.com/settings/system-users/?business_id=2100949430186290 |
| WhatsApp Manager | business.facebook.com/latest/whatsapp_manager/phone_numbers/?business_id=2100949430186290 |
| Meta Business Inbox | business.facebook.com/latest/inbox |
| Cloud API Docs | developers.facebook.com/docs/whatsapp/cloud-api |
| Pricing | developers.facebook.com/docs/whatsapp/pricing |

---

## Decisões Pendentes

- [ ] Registrar número (verificação em progresso)
- [ ] Gerar token permanente via System User
- [ ] Configurar webhook no Meta + implementar endpoint na business-api
- [ ] Publicar app no Meta (necessário pra receber webhooks de produção)
- [ ] Criar e submeter template messages pra aprovação
- [ ] Implementar handler de mensagens na business-api
- [ ] Definir flow do bot (reutilizar form JSON ou novo)
- [ ] Adicionar método de pagamento na conta WhatsApp Business (pra mensagens business-initiated)
- [ ] Corrigir nome de exibição (BooPoixel → BooPixel)
