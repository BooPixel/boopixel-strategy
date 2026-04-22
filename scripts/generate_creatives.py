"""
BooPixel — Ad Creative Generator

Gera criativos para Meta Ads e Google Ads a partir dos planos cadastrados no banco.
Formatos: Feed (1080x1080), Stories (1080x1920)

Uso:
    python scripts/generate_creatives.py
    python scripts/generate_creatives.py --plan essential
    python scripts/generate_creatives.py --format stories
    python scripts/generate_creatives.py --output ./output

Requer:
    pip install Pillow sqlalchemy pymysql python-dotenv
"""

import os
import argparse
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import create_engine, text

load_dotenv(os.path.expanduser("~/.env"))

ENGINE = create_engine(os.environ["DATABASE_URL"])

FORMATS = {
    "feed": (1080, 1080),
    "stories": (1080, 1920),
}

COLORS = {
    "bg": "#0a0a1a",
    "card": "#141428",
    "accent": "#6c5ce7",
    "accent_light": "#a29bfe",
    "text": "#ffffff",
    "text_muted": "#b2b2cc",
    "price": "#00e676",
    "badge": "#ff6b6b",
}

CATEGORY_LABELS = {
    "maintenance": "Manutencao",
    "premium": "Premium",
    "addon": "Addon",
}


def get_plans(slug_filter=None):
    with ENGINE.connect() as conn:
        query = """
            SELECT p.slug, p.name, p.price_monthly, p.price_yearly, p.is_featured,
                   pc.slug as category,
                   GROUP_CONCAT(
                       CONCAT(o.name, ' — ', pi.limit_note)
                       ORDER BY o.id SEPARATOR '|'
                   ) as items
            FROM plans p
            LEFT JOIN plan_categories pc ON p.category_id = pc.id
            LEFT JOIN plan_items pi ON pi.plan_id = p.id
            LEFT JOIN offerings o ON pi.offering_id = o.id
            WHERE p.is_active = 1
        """
        params = {}
        if slug_filter:
            query += " AND p.slug = :slug"
            params["slug"] = slug_filter
        query += " GROUP BY p.id ORDER BY pc.sort_order, p.tier"
        rows = conn.execute(text(query), params).fetchall()
    return rows


def get_font(size, bold=False):
    """Try system fonts, fallback to default."""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/Arial.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90, fill=fill)


def format_price(value):
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def generate_plan_creative(plan, fmt_name, fmt_size, output_dir):
    slug, name, monthly, yearly, featured, category, items_raw = plan
    w, h = fmt_size

    img = Image.new("RGBA", (w, h), COLORS["bg"])
    draw = ImageDraw.Draw(img)

    font_brand = get_font(28)
    font_category = get_font(22)
    font_name = get_font(64, bold=True)
    font_price = get_font(48, bold=True)
    font_yearly = get_font(24)
    font_item = get_font(26)
    font_cta = get_font(32, bold=True)

    # Y offset based on format
    y = 60 if fmt_name == "feed" else 200

    # Brand
    draw.text((80, y), "BOOPIXEL", font=font_brand, fill=COLORS["accent_light"])
    y += 50

    # Category badge
    cat_label = CATEGORY_LABELS.get(category, category or "")
    if cat_label:
        draw.text((80, y), cat_label.upper(), font=font_category, fill=COLORS["text_muted"])
        y += 40

    # Plan name
    draw.text((80, y), name, font=font_name, fill=COLORS["text"])
    y += 90

    # Featured badge
    if featured:
        draw_rounded_rect(draw, (80, y, 260, y + 36), 18, COLORS["badge"])
        draw.text((100, y + 4), "MAIS POPULAR", font=font_category, fill=COLORS["text"])
        y += 50

    # Price
    price_text = f"{format_price(monthly)}/mes"
    draw.text((80, y), price_text, font=font_price, fill=COLORS["price"])
    y += 65

    # Yearly
    yearly_text = f"ou {format_price(yearly)}/ano"
    draw.text((80, y), yearly_text, font=font_yearly, fill=COLORS["text_muted"])
    y += 50

    # Divider
    draw.line([(80, y), (w - 80, y)], fill=COLORS["accent"], width=2)
    y += 30

    # Items
    if items_raw:
        items = items_raw.split("|")
        max_items = 6 if fmt_name == "feed" else 10
        for item in items[:max_items]:
            parts = item.split(" — ")
            item_name = parts[0].strip() if parts else item
            item_note = parts[1].strip() if len(parts) > 1 else ""
            draw.text((100, y), f"•  {item_name}", font=font_item, fill=COLORS["text"])
            if item_note:
                y += 32
                draw.text((120, y), item_note, font=font_yearly, fill=COLORS["text_muted"])
            y += 38

        if len(items) > max_items:
            draw.text((100, y), f"+ {len(items) - max_items} mais...", font=font_yearly, fill=COLORS["accent_light"])
            y += 38

    # CTA button
    cta_y = h - 140 if fmt_name == "stories" else h - 120
    draw_rounded_rect(draw, (80, cta_y, w - 80, cta_y + 64), 32, COLORS["accent"])
    cta_text = "Ver planos"
    bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
    cta_tw = bbox[2] - bbox[0]
    draw.text(((w - cta_tw) // 2, cta_y + 14), cta_text, font=font_cta, fill=COLORS["text"])

    # URL
    draw.text((80, cta_y + 80), "app.boopixel.com/pricing", font=font_yearly, fill=COLORS["text_muted"])

    # Save
    filename = f"ad_{slug}_{fmt_name}.png"
    filepath = output_dir / filename
    img.save(filepath, "PNG")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="BooPixel Ad Creative Generator")
    parser.add_argument("--plan", help="Gerar apenas para um plano (slug)")
    parser.add_argument("--format", choices=["feed", "stories"], help="Gerar apenas um formato")
    parser.add_argument("--output", default="scripts/output", help="Diretorio de saida")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    plans = get_plans(args.plan)
    if not plans:
        print("Nenhum plano encontrado")
        return

    formats = {args.format: FORMATS[args.format]} if args.format else FORMATS
    count = 0

    for plan in plans:
        for fmt_name, fmt_size in formats.items():
            path = generate_plan_creative(plan, fmt_name, fmt_size, output_dir)
            print(f"  {path}")
            count += 1

    print(f"\n{count} criativos gerados em {output_dir}/")
    print(f"Timestamp: {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
