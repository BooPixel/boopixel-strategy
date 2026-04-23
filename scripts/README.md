# BooPixel Scripts

Scripts Python para automação de marketing, ads e comunicação.

## Requisitos

```bash
pip install requests python-dotenv Pillow fpdf2 google-ads
```

Credenciais em `~/.env` — ver cada script para variáveis necessárias.

---

## WhatsApp Cloud API (`whatsapp.py`)

Envio de mensagens, templates, imagens, documentos e botões via WhatsApp Business API.

### Variáveis necessárias (em ~/.env)

```
WHATSAPP_TOKEN=<token permanente do System User>
WHATSAPP_PHONE_NUMBER_ID=1011433038730788
WHATSAPP_WABA_ID=2693966874336487
```

### Comandos

```bash
# Enviar texto (destinatário precisa ter mandado mensagem antes — janela 24h)
python scripts/whatsapp.py send 5548999897204 "Olá, tudo bem?"

# Enviar template (pode iniciar conversa, precisa de template aprovado)
python scripts/whatsapp.py template 5548999897204 lead_welcome pt_BR "João"

# Enviar imagem com legenda
python scripts/whatsapp.py image 5548999897204 https://example.com/foto.jpg "Veja nosso portfolio"

# Enviar documento (PDF, DOC)
python scripts/whatsapp.py document 5548999897204 https://example.com/proposta.pdf "Proposta BooPixel"

# Enviar botões interativos (max 3)
python scripts/whatsapp.py button 5548999897204 "Qual plano te interessa?" "Essential,Professional,Advanced"

# Enviar lista de opções
python scripts/whatsapp.py list 5548999897204 "Nossos serviços:" "Ver opções" '[{"title":"Planos","rows":[{"id":"1","title":"Essential","description":"R$ 250/mês"},{"id":"2","title":"Professional","description":"R$ 497/mês"}]}]'

# Ver info do número registrado
python scripts/whatsapp.py info

# Listar templates disponíveis
python scripts/whatsapp.py templates

# Marcar mensagem como lida
python scripts/whatsapp.py read wamid.HBgMNTU0ODk5ODk3MjA0...
```

### Notas

- **Mensagem de texto** só funciona se o destinatário mandou mensagem nas últimas 24h
- **Template message** pode iniciar conversa, mas precisa ser aprovado pelo Meta antes
- **Botões** max 3, cada label max 20 caracteres
- **Lista** max 10 itens por seção, max 10 seções

---

## Google Ads API (`test_google_ads.py`)

Testa conexão com Google Ads API.

### Variáveis necessárias

```
ADS_CLIENT_ID, ADS_CLIENT_SECRET, ADS_REFRESH_TOKEN
ADS_DEVELOPER_TOKEN, ADS_CUSTOMER_ID, ADS_MCC_ID
```

### Uso

```bash
python scripts/test_google_ads.py
```

> Requer Basic Access aprovado (solicitado em 2026-04-22).

---

## Google Ads OAuth (`generate_ads_token.py`)

Gera refresh token via OAuth Desktop flow.

```bash
python scripts/generate_ads_token.py
```

Abre browser → logar com conta do MCC → token aparece no terminal.

---

## Google Ads API Design Doc (`generate_api_doc.py`)

Gera PDF de design document para aplicação de Basic Access.

```bash
python scripts/generate_api_doc.py
# Output: scripts/output/google_ads_api_design.pdf
```

---

## Meta Ads — Gerador de Criativos (`generate_creatives.py`)

Gera imagens para campanhas Meta Ads usando Pillow.

```bash
python scripts/generate_creatives.py
```

---

## Meta Ads — Publisher (`publish_meta.py`)

Publica campanhas no Meta Ads via API.

### Variáveis necessárias

```
META_APP_ID, META_ACCESS_TOKEN, META_AD_ACCOUNT_ID, META_PAGE_ID
```

```bash
python scripts/publish_meta.py
```

---

## Meta Ads — Deploy Campaign (`deploy_meta_campaign.py`)

Deploy de campanha completa no Meta Ads.

```bash
python scripts/deploy_meta_campaign.py
```
