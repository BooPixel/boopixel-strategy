"""
BooPixel — Meta Ads Publisher

Publica criativos gerados pelo generate_creatives.py no Meta Ads.
Requer facebook-business SDK e token configurado.

Uso:
    python scripts/publish_meta.py
    python scripts/publish_meta.py --plan essential --format feed
    python scripts/publish_meta.py --dry-run

Requer:
    pip install facebook-business python-dotenv

Env vars (~/.env):
    META_APP_ID
    META_APP_SECRET
    META_ACCESS_TOKEN
    META_AD_ACCOUNT_ID
    META_PAGE_ID
"""

import os
import argparse
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.env"))

META_APP_ID = os.environ.get("META_APP_ID")
META_APP_SECRET = os.environ.get("META_APP_SECRET")
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")
META_AD_ACCOUNT_ID = os.environ.get("META_AD_ACCOUNT_ID")
META_PAGE_ID = os.environ.get("META_PAGE_ID")

PRICING_URL = "https://app.boopixel.com/pricing"


def upload_image(api, ad_account_id, filepath):
    from facebook_business.adobjects.adimage import AdImage

    image = AdImage(parent_id=ad_account_id)
    image[AdImage.Field.filename] = str(filepath)
    image.remote_create()
    return image[AdImage.Field.hash]


def create_creative(api, ad_account_id, page_id, image_hash, name, message):
    from facebook_business.adobjects.adcreative import AdCreative

    creative = AdCreative(parent_id=ad_account_id)
    creative[AdCreative.Field.name] = name
    creative[AdCreative.Field.object_story_spec] = {
        "page_id": page_id,
        "link_data": {
            "image_hash": image_hash,
            "link": PRICING_URL,
            "message": message,
            "call_to_action": {"type": "LEARN_MORE"},
        },
    }
    creative.remote_create()
    return creative["id"]


PLAN_MESSAGES = {
    "essential": "Sites profissionais a partir de R$ 250/mes. Dominio + SSL + Email + Backup incluso.",
    "professional": "Site + SEO + Relatorio mensal por R$ 497/mes. Cresca no Google.",
    "advanced": "SEO completo + Google Analytics por R$ 797/mes. Resultados reais.",
    "business": "Site + SEO + Landing Pages + Trafego pago por R$ 1.497/mes.",
    "growth": "Tudo do Business + Consultoria mensal por R$ 2.497/mes.",
    "enterprise": "Solucao completa para sua empresa. A partir de R$ 3.997/mes.",
    "ai-agent": "Agente IA para WhatsApp + Chat. Atendimento 24/7 por R$ 997/mes.",
    "automation": "Automatize processos da sua empresa por R$ 1.497/mes.",
}


def main():
    parser = argparse.ArgumentParser(description="BooPixel Meta Ads Publisher")
    parser.add_argument("--plan", help="Publicar apenas um plano (slug)")
    parser.add_argument("--format", choices=["feed", "stories"], help="Apenas um formato")
    parser.add_argument("--input", default="scripts/output", help="Diretorio dos criativos")
    parser.add_argument("--dry-run", action="store_true", help="Simular sem publicar")
    args = parser.parse_args()

    input_dir = Path(args.input)
    if not input_dir.exists():
        print(f"Diretorio {input_dir} nao encontrado. Execute generate_creatives.py primeiro.")
        return

    images = sorted(input_dir.glob("ad_*.png"))
    if args.plan:
        images = [i for i in images if f"ad_{args.plan}_" in i.name]
    if args.format:
        images = [i for i in images if f"_{args.format}.png" in i.name]

    if not images:
        print("Nenhum criativo encontrado")
        return

    if args.dry_run:
        print("DRY RUN — nao vai publicar\n")
        for img in images:
            slug = img.stem.replace("ad_", "").rsplit("_", 1)[0]
            msg = PLAN_MESSAGES.get(slug, "")
            print(f"  {img.name} -> {msg[:60]}...")
        print(f"\n{len(images)} criativos seriam publicados")
        return

    if not all([META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN, META_AD_ACCOUNT_ID, META_PAGE_ID]):
        print("Faltam env vars META_*. Configure no ~/.env:")
        print("  META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN, META_AD_ACCOUNT_ID, META_PAGE_ID")
        return

    from facebook_business.api import FacebookAdsApi

    api = FacebookAdsApi.init(META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN)

    count = 0
    for img in images:
        slug = img.stem.replace("ad_", "").rsplit("_", 1)[0]
        fmt = img.stem.rsplit("_", 1)[1]
        message = PLAN_MESSAGES.get(slug, f"Plano {slug} — BooPixel")
        creative_name = f"BooPixel — {slug} — {fmt}"

        print(f"  Uploading {img.name}...")
        image_hash = upload_image(api, META_AD_ACCOUNT_ID, img)

        print(f"  Creating creative: {creative_name}")
        creative_id = create_creative(
            api, META_AD_ACCOUNT_ID, META_PAGE_ID, image_hash, creative_name, message
        )
        print(f"  Creative ID: {creative_id}")
        count += 1

    print(f"\n{count} criativos publicados no Meta Ads")


if __name__ == "__main__":
    main()
