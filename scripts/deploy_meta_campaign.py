"""
BooPixel — Meta Ads Campaign Deployer

Cria campanha completa no Meta Ads: Campaign → Ad Set → Ad Creative → Ad.
Usa criativos gerados pelo generate_creatives.py.

Uso:
    python scripts/deploy_meta_campaign.py --plan essential --budget 50
    python scripts/deploy_meta_campaign.py --plan essential --budget 50 --dry-run
    python scripts/deploy_meta_campaign.py --list

Requer:
    pip install facebook-business Pillow sqlalchemy pymysql python-dotenv

Env vars (~/.env):
    META_ACCESS_TOKEN
    META_AD_ACCOUNT_ID
    DATABASE_URL
"""

import os
import argparse
from pathlib import Path

from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.adcreative import AdCreative
from sqlalchemy import create_engine, text

load_dotenv(os.path.expanduser("~/.env"))

ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
AD_ACCOUNT_ID = os.environ["META_AD_ACCOUNT_ID"]
PAGE_ID = os.environ["META_PAGE_ID"]
ENGINE = create_engine(os.environ["DATABASE_URL"])
PRICING_URL = "https://app.boopixel.com/pricing"
CREATIVE_DIR = Path("scripts/output")

PLAN_AD_COPY = {
    "essential": {
        "title": "Site Profissional — R$ 250/mes",
        "body": "Site + dominio + SSL + email + backup incluso. Tudo que sua empresa precisa online. Veja nossos planos.",
    },
    "professional": {
        "title": "Site + SEO — R$ 497/mes",
        "body": "Site profissional com SEO, relatorio mensal e 10 contas de email. Apareca no Google. Veja nossos planos.",
    },
    "advanced": {
        "title": "Site + SEO Completo — R$ 797/mes",
        "body": "SEO completo com Google Analytics, backup diario e ate 10 paginas. Resultados reais. Veja nossos planos.",
    },
    "business": {
        "title": "Site + SEO + Landing Pages — R$ 1.497/mes",
        "body": "Tudo do Professional + trafego pago + ate 2 landing pages por mes. Cresca de verdade. Veja nossos planos.",
    },
    "growth": {
        "title": "Cresca com BooPixel — R$ 2.497/mes",
        "body": "SEO completo + trafego pago + consultoria mensal + 5 landing pages/mes. Seu parceiro digital. Veja nossos planos.",
    },
    "enterprise": {
        "title": "Solucao Completa — R$ 3.997/mes",
        "body": "Tudo incluso: site, SEO, trafego pago, consultoria, LPs ilimitadas. A solucao definitiva. Veja nossos planos.",
    },
    "ai-agent": {
        "title": "Agente IA WhatsApp — R$ 997/mes",
        "body": "Atendimento 24/7 automatico no WhatsApp e Chat. Agente IA treinado com os dados da sua empresa. Veja nossos planos.",
    },
    "automation": {
        "title": "Automacao de Processos — R$ 1.497/mes",
        "body": "Automatize tarefas repetitivas da sua empresa. Mais produtividade, menos trabalho manual. Veja nossos planos.",
    },
}

CAMPAIGN_CONFIGS = {
    "maintenance": {
        "name": "BooPixel — Sites e Manutencao",
        "objective": "OUTCOME_LEADS",
        "daily_budget": None,  # set per plan
        "age_min": 25,
        "age_max": 55,
        "interests": [
            {"id": "6003139266461", "name": "Small business"},
            {"id": "6003384248805", "name": "Entrepreneurship"},
            {"id": "6003397425735", "name": "Web design"},
        ],
    },
    "premium": {
        "name": "BooPixel — Projetos Premium",
        "objective": "OUTCOME_LEADS",
        "daily_budget": None,
        "age_min": 28,
        "age_max": 55,
        "interests": [
            {"id": "6003139266461", "name": "Small business"},
            {"id": "6003384248805", "name": "Entrepreneurship"},
            {"id": "6003020834693", "name": "Digital marketing"},
        ],
    },
    "addon": {
        "name": "BooPixel — IA e Automacao",
        "objective": "OUTCOME_LEADS",
        "daily_budget": None,
        "age_min": 25,
        "age_max": 50,
        "interests": [
            {"id": "6003139266461", "name": "Small business"},
            {"id": "6003966541831", "name": "Artificial intelligence"},
            {"id": "6003349442455", "name": "Automation"},
        ],
    },
}


def get_plan(slug):
    with ENGINE.connect() as conn:
        row = conn.execute(
            text("""
                SELECT p.slug, p.name, p.price_monthly, p.price_yearly, pc.slug as category
                FROM plans p
                LEFT JOIN plan_categories pc ON p.category_id = pc.id
                WHERE p.slug = :slug AND p.is_active = 1
            """),
            {"slug": slug},
        ).fetchone()
    return row


def list_plans():
    with ENGINE.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT p.slug, p.name, p.price_monthly, pc.slug as category
                FROM plans p
                LEFT JOIN plan_categories pc ON p.category_id = pc.id
                WHERE p.is_active = 1
                ORDER BY pc.sort_order, p.tier
            """)
        ).fetchall()
    print("Planos disponiveis:\n")
    for r in rows:
        print(f"  {r[0]:<15} | {r[1]:<15} | R$ {float(r[2]):>8,.2f}/mes | {r[3]}")


def ensure_creative(slug):
    feed = CREATIVE_DIR / f"ad_{slug}_feed.png"
    stories = CREATIVE_DIR / f"ad_{slug}_stories.png"
    if not feed.exists() or not stories.exists():
        print(f"  Gerando criativos para {slug}...")
        os.system(f"python3 scripts/generate_creatives.py --plan {slug}")
    return feed, stories


def deploy(slug, daily_budget_brl, dry_run=False):
    plan = get_plan(slug)
    if not plan:
        print(f"Plano '{slug}' nao encontrado")
        return

    plan_slug, plan_name, price_monthly, price_yearly, category = plan
    config = CAMPAIGN_CONFIGS.get(category)
    if not config:
        print(f"Categoria '{category}' nao tem config de campanha")
        return

    ad_copy = PLAN_AD_COPY.get(slug, {"title": plan_name, "body": f"Plano {plan_name} — BooPixel"})
    budget_cents = int(daily_budget_brl * 100)

    print(f"\n{'DRY RUN — ' if dry_run else ''}Deploy: {plan_name}")
    print(f"  Categoria: {category}")
    print(f"  Budget: R$ {daily_budget_brl}/dia (R$ {daily_budget_brl * 30:,.0f}/mes)")
    print(f"  Objetivo: {config['objective']}")
    print(f"  Titulo: {ad_copy['title']}")
    print(f"  Body: {ad_copy['body'][:60]}...")
    print(f"  URL: {PRICING_URL}")

    if dry_run:
        print("\n  [DRY RUN] Nada criado.")
        return

    # Init API
    FacebookAdsApi.init(access_token=ACCESS_TOKEN)
    account = AdAccount(AD_ACCOUNT_ID)

    # 1. Campaign
    print("\n  1/5 Criando campanha...")
    campaign = account.create_campaign(params={
        "name": f"{config['name']} — {plan_name}",
        "objective": config["objective"],
        "status": "PAUSED",
        "special_ad_categories": [],
        "is_adset_budget_sharing_enabled": False,
    })
    campaign_id = campaign.get_id()
    print(f"      Campaign ID: {campaign_id}")

    # 2. Ad Set
    print("  2/5 Criando ad set...")
    ad_set = account.create_ad_set(params={
        "name": f"{plan_name} — Feed + Stories",
        "campaign_id": campaign_id,
        "daily_budget": budget_cents,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "LEAD_GENERATION",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "targeting": {
            "geo_locations": {"countries": ["BR"]},
            "age_min": config["age_min"],
            "age_max": config["age_max"],
            "flexible_spec": [{"interests": config["interests"]}],
            "publisher_platforms": ["facebook", "instagram"],
            "facebook_positions": ["feed"],
            "instagram_positions": ["stream", "story", "reels"],
            "targeting_automation": {"advantage_audience": 0},
        },
        "status": "PAUSED",
    })
    ad_set_id = ad_set.get_id()
    print(f"      Ad Set ID: {ad_set_id}")

    # 3. Upload image
    print("  3/5 Fazendo upload do criativo...")
    feed_img, _ = ensure_creative(slug)
    image = AdImage(parent_id=AD_ACCOUNT_ID)
    image[AdImage.Field.filename] = str(feed_img)
    image.remote_create()
    image_hash = image[AdImage.Field.hash]
    print(f"      Image hash: {image_hash}")

    # 4. Ad Creative
    print("  4/5 Criando ad creative...")
    creative = account.create_ad_creative(params={
        "name": f"Creative — {plan_name} — Feed",
        "object_story_spec": {
            "page_id": PAGE_ID,
            "link_data": {
                "image_hash": image_hash,
                "link": PRICING_URL,
                "message": ad_copy["body"],
                "name": ad_copy["title"],
                "call_to_action": {"type": "LEARN_MORE", "value": {"link": PRICING_URL}},
            },
        },
    })
    creative_id = creative.get_id()
    print(f"      Creative ID: {creative_id}")

    # 5. Ad
    print("  5/5 Criando ad...")
    ad = account.create_ad(params={
        "name": f"Ad — {plan_name}",
        "adset_id": ad_set_id,
        "creative": {"creative_id": creative_id},
        "status": "PAUSED",
    })
    ad_id = ad.get_id()
    print(f"      Ad ID: {ad_id}")

    print(f"\n  Campanha criada com sucesso (PAUSED)")
    print(f"  Para ativar, mude o status para ACTIVE no Meta Ads Manager")
    print(f"  https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT_ID.replace('act_', '')}")

    return {
        "campaign_id": campaign_id,
        "ad_set_id": ad_set_id,
        "creative_id": creative_id,
        "ad_id": ad_id,
    }


def main():
    parser = argparse.ArgumentParser(description="BooPixel Meta Ads Campaign Deployer")
    parser.add_argument("--plan", help="Slug do plano (ex: essential)")
    parser.add_argument("--budget", type=float, default=50, help="Budget diario em R$ (default: 50)")
    parser.add_argument("--dry-run", action="store_true", help="Simular sem criar")
    parser.add_argument("--list", action="store_true", help="Listar planos disponiveis")
    args = parser.parse_args()

    if args.list:
        list_plans()
        return

    if not args.plan:
        print("Use --plan <slug> ou --list para ver planos")
        return

    deploy(args.plan, args.budget, args.dry_run)


if __name__ == "__main__":
    main()
