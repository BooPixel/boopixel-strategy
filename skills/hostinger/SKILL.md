---
name: hostinger
description: Manage Hostinger account via API. Use when the user asks to list websites, domains, DNS records, subscriptions, billing, VPS, Docker, or any Hostinger hosting operation.
version: 1.0.0
allowed-tools: Bash, Read, Edit, Write, Glob, Grep
---

You are an expert assistant for managing **Hostinger** via the official API. Execute requests directly using curl.

**API Docs:** https://developers.hostinger.com/
**Token location:** `~/.env` as `HOSTINGER_API_TOKEN`

---

## Connection

```bash
# Load token
TOKEN=$(grep HOSTINGER_API_TOKEN ~/.env | cut -d= -f2)
BASE="https://developers.hostinger.com"

# Example request
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/hosting/v1/websites" | python3 -m json.tool
```

For Python:

```python
import os
from dotenv import load_dotenv
import requests

load_dotenv(os.path.expanduser("~/.env"))
TOKEN = os.environ["HOSTINGER_API_TOKEN"]
BASE = "https://developers.hostinger.com"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

r = requests.get(f"{BASE}/api/hosting/v1/websites", headers=HEADERS)
print(r.json())
```

---

## API Endpoints

### Hosting

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hosting/v1/websites` | List all websites (paginated) |
| POST | `/api/hosting/v1/websites` | Create new website |
| GET | `/api/hosting/v1/orders` | List hosting orders |
| GET | `/api/hosting/v1/datacenters` | List available datacenters |
| POST | `/api/hosting/v1/domains/free-subdomains` | Generate free subdomain |
| POST | `/api/hosting/v1/domains/verify-ownership` | Verify domain ownership |

**Websites params:** `page`, `per_page`, `username`, `order_id`, `is_enabled`, `domain_filter`

### Domains

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/domains/v1/portfolio` | List all domains |
| GET | `/api/domains/v1/portfolio/{domain}` | Domain details |
| POST | `/api/domains/v1/portfolio` | Purchase/register domain |
| PUT | `/api/domains/v1/portfolio/{domain}/nameservers` | Set nameservers |
| PUT | `/api/domains/v1/portfolio/{domain}/domain-lock` | Enable domain lock |
| DELETE | `/api/domains/v1/portfolio/{domain}/domain-lock` | Disable domain lock |
| PUT | `/api/domains/v1/portfolio/{domain}/privacy-protection` | Enable WHOIS privacy |
| DELETE | `/api/domains/v1/portfolio/{domain}/privacy-protection` | Disable WHOIS privacy |
| POST | `/api/domains/v1/availability` | Check domain availability |

### Domain Forwarding

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/domains/v1/forwarding/{domain}` | Get forwarding config |
| POST | `/api/domains/v1/forwarding` | Create forwarding/redirect |
| DELETE | `/api/domains/v1/forwarding/{domain}` | Delete forwarding |

### DNS

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dns/v1/zones/{domain}` | Get DNS records |
| PUT | `/api/dns/v1/zones/{domain}` | Update DNS records |
| DELETE | `/api/dns/v1/zones/{domain}` | Delete DNS records |
| POST | `/api/dns/v1/zones/{domain}/reset` | Reset DNS to default |
| POST | `/api/dns/v1/zones/{domain}/validate` | Validate DNS before applying |
| GET | `/api/dns/v1/snapshots/{domain}` | List DNS snapshots |
| GET | `/api/dns/v1/snapshots/{domain}/{snapshotId}` | Get snapshot details |
| POST | `/api/dns/v1/snapshots/{domain}/{snapshotId}/restore` | Restore DNS snapshot |

### Billing

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/billing/v1/catalog` | List catalog items (params: `category`, `name`) |
| GET | `/api/billing/v1/subscriptions` | List all subscriptions |
| PATCH | `/api/billing/v1/subscriptions/{id}/auto-renewal/enable` | Enable auto-renewal |
| DELETE | `/api/billing/v1/subscriptions/{id}/auto-renewal/disable` | Disable auto-renewal |
| GET | `/api/billing/v1/payment-methods` | List payment methods |
| POST | `/api/billing/v1/payment-methods/{id}` | Set primary payment method |
| DELETE | `/api/billing/v1/payment-methods/{id}` | Remove payment method |

### WHOIS Profiles

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/domains/v1/whois` | List WHOIS profiles (param: `tld`) |
| GET | `/api/domains/v1/whois/{whoisId}` | Get profile details |
| POST | `/api/domains/v1/whois` | Create WHOIS profile |
| DELETE | `/api/domains/v1/whois/{whoisId}` | Delete WHOIS profile |
| GET | `/api/domains/v1/whois/{whoisId}/usage` | List domains using profile |

### Email Marketing (Reach)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reach/v1/profiles` | List email profiles |
| GET | `/api/reach/v1/contacts` | List contacts (deprecated) |
| POST | `/api/reach/v1/contacts` | Create contact (deprecated) |
| DELETE | `/api/reach/v1/contacts/{uuid}` | Delete contact |
| POST | `/api/reach/v1/profiles/{profileUuid}/contacts` | Create contact (new) |
| GET | `/api/reach/v1/contacts/groups` | List contact groups |
| GET | `/api/reach/v1/segmentation/segments` | List segments |
| POST | `/api/reach/v1/segmentation/segments` | Create segment |
| GET | `/api/reach/v1/segmentation/segments/{uuid}` | Get segment |
| GET | `/api/reach/v1/segmentation/segments/{uuid}/contacts` | List segment contacts |

### VPS

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vps/v1/data-centers` | List VPS datacenters |
| GET | `/api/vps/v1/virtual-machines/{vmId}/docker` | List Docker projects |
| POST | `/api/vps/v1/virtual-machines/{vmId}/docker` | Deploy Docker project |
| GET | `/api/vps/v1/virtual-machines/{vmId}/docker/{project}` | Get project details |
| DELETE | `/api/vps/v1/virtual-machines/{vmId}/docker/{project}/down` | Remove project |
| GET | `/api/vps/v1/virtual-machines/{vmId}/docker/{project}/containers` | List containers |
| GET | `/api/vps/v1/virtual-machines/{vmId}/docker/{project}/logs` | Get project logs |
| POST | `/api/vps/v1/virtual-machines/{vmId}/docker/{project}/restart` | Restart project |

### Domain Verifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/direct/verifications/active` | List pending/completed verifications |

---

## Common Recipes

### List all websites
```bash
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/hosting/v1/websites" | python3 -m json.tool
```

### List all domains
```bash
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/domains/v1/portfolio" | python3 -m json.tool
```

### Get DNS records for a domain
```bash
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/dns/v1/zones/boopixel.com" | python3 -m json.tool
```

### Check domain availability
```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"domain":"example","tlds":["com","com.br","net"]}' \
  "$BASE/api/domains/v1/availability" | python3 -m json.tool
```

### List subscriptions/billing
```bash
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/billing/v1/subscriptions" | python3 -m json.tool
```

---

## Known Account Data

**Account websites (27 total):**

Domains proprios:
- boopixel.com (main) + boopixel.com.br (addon)
- system.boopixel.com, email.boopixel.com, cliente.boopixel.com (subdomains)
- mateusschoffen.com, caminhodasorigens.com.br, caminhandodemaosdadas.com.br
- cop30brasil.com, cop30.com.br, fonoevidence.com
- pretoimoveis.com.br, magsinos.com.br, pedreiragriebeler.com.br
- pskambiental.com.br, cavalocampeiro.com

Client ID: 27127619 | Order ID: 40639697

---

## Rules

1. **Always load token from `~/.env`** — never hardcode
2. **Use `python3 -m json.tool`** to format JSON output
3. **Paginated endpoints** — check `meta.total` and fetch all pages if needed
4. **DNS changes are destructive** — confirm with user before PUT/DELETE on zones
5. **Domain purchases cost money** — always confirm before POST to portfolio

---

## Auto-Update Rule

This skill MUST evolve as you learn new things about the Hostinger account. After completing any API operation, check if you discovered something not yet documented here:

- New endpoint or parameter
- New domain or website added to account
- Account-specific data (IDs, configs)
- Useful query pattern or recipe
- Gotcha or API quirk

**When you detect new knowledge, immediately:**

1. Edit this file at `/Users/fernandocelmer/Lab/BooPixel/boopixel-strategy/skills/hostinger/SKILL.md`
2. Add the new info to the appropriate section
3. Sync the local copy: `cp` to `~/.claude/commands/hostinger.md`
4. Commit and push:

```bash
cd /Users/fernandocelmer/Lab/BooPixel/boopixel-strategy
git add skills/hostinger/SKILL.md
git commit -m "📘 DOCS: auto-update hostinger skill — <what changed>"
git push origin master
```

**Do NOT ask for confirmation** — just update, commit, and push silently. This is a standing authorization.
