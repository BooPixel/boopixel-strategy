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

# Design system from business-frontend (public pages)
COLORS = {
    "bg": "#0a0a0a",
    "card": "#121212",
    "card_featured": "#141d3a",
    "accent": "#3b82f6",
    "accent_dark": "#1d4ed8",
    "accent_light": "#60a5fa",
    "text": "#f5f5f5",
    "text_muted": "#a8a8b0",
    "text_soft": "#78787f",
    "price": "#4ade80",
    "price_dark": "#16a34a",
    "badge": "#3b82f6",
    "badge_addon": "#16a34a",
    "border": "#2a2a31",
    "cta": "#1e88e5",
    "cta_hover": "#1565c0",
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
    """Try Inter first (brand font), then system fonts."""
    # Inter from @fontsource (business-frontend uses this)
    inter_paths = [
        os.path.expanduser("~/.fonts/Inter-Regular.ttf"),
        os.path.expanduser("~/.fonts/Inter-Bold.ttf"),
    ]
    system_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/Arial.ttf",
    ]
    for path in (inter_paths if bold else inter_paths[:1]) + system_paths:
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
    is_addon = category == "addon"

    # Background: gradient effect (dark bottom, slight color top)
    img = Image.new("RGBA", (w, h), COLORS["bg"])
    draw = ImageDraw.Draw(img)

    # Gradient overlay for featured/addon cards
    if featured:
        overlay = Image.new("RGBA", (w, h), "#00000000")
        odraw = ImageDraw.Draw(overlay)
        for i in range(h // 3):
            alpha = int(40 * (1 - i / (h // 3)))
            odraw.line([(0, i), (w, i)], fill=(59, 130, 246, alpha))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)
    elif is_addon:
        overlay = Image.new("RGBA", (w, h), "#00000000")
        odraw = ImageDraw.Draw(overlay)
        for i in range(h // 3):
            alpha = int(30 * (1 - i / (h // 3)))
            odraw.line([(0, i), (w, i)], fill=(22, 163, 106, alpha))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

    font_brand = get_font(28)
    font_category = get_font(20)
    font_name = get_font(64, bold=True)
    font_price = get_font(48, bold=True)
    font_yearly = get_font(22)
    font_item = get_font(24)
    font_item_note = get_font(20)
    font_cta = get_font(30, bold=True)
    font_url = get_font(20)

    margin = 80
    y = 60 if fmt_name == "feed" else 180

    # Brand name
    draw.text((margin, y), "BOOPIXEL", font=font_brand, fill=COLORS["accent_light"])
    y += 50

    # Category badge pill
    cat_label = CATEGORY_LABELS.get(category, category or "").upper()
    if cat_label:
        bbox = draw.textbbox((0, 0), cat_label, font=font_category)
        cat_w = bbox[2] - bbox[0] + 24
        badge_color = COLORS["badge_addon"] if is_addon else COLORS["border"]
        draw_rounded_rect(draw, (margin, y, margin + cat_w, y + 30), 15, badge_color)
        draw.text((margin + 12, y + 4), cat_label, font=font_category, fill=COLORS["text"])
        y += 46

    # Plan name
    draw.text((margin, y), name, font=font_name, fill=COLORS["text"])
    y += 85

    # Featured badge
    if featured:
        draw_rounded_rect(draw, (margin, y, margin + 190, y + 32), 16, COLORS["accent"])
        draw.text((margin + 14, y + 4), "MAIS POPULAR", font=font_category, fill=COLORS["text"])
        y += 48

    # Price
    price_text = f"{format_price(monthly)}/mes"
    draw.text((margin, y), price_text, font=font_price, fill=COLORS["price"])
    y += 60

    # Yearly price
    yearly_text = f"ou {format_price(yearly)}/ano"
    draw.text((margin, y), yearly_text, font=font_yearly, fill=COLORS["text_soft"])
    y += 44

    # Divider line
    draw.line([(margin, y), (w - margin, y)], fill=COLORS["border"], width=1)
    y += 24

    # Items list
    if items_raw:
        items = items_raw.split("|")
        max_items = 5 if fmt_name == "feed" else 9
        for item in items[:max_items]:
            parts = item.split(" — ")
            item_name = parts[0].strip() if parts else item
            item_note = parts[1].strip() if len(parts) > 1 else ""

            # Checkmark
            check_color = COLORS["price"] if not is_addon else COLORS["badge_addon"]
            draw.text((margin + 4, y), "\u2713", font=font_item, fill=check_color)
            draw.text((margin + 32, y), item_name, font=font_item, fill=COLORS["text"])
            y += 30
            if item_note:
                draw.text((margin + 32, y), item_note, font=font_item_note, fill=COLORS["text_muted"])
                y += 26
            y += 8

        if len(items) > max_items:
            remaining = len(items) - max_items
            draw.text((margin + 32, y), f"+ {remaining} mais...", font=font_item_note, fill=COLORS["accent_light"])
            y += 34

    # CTA button
    cta_y = h - 130 if fmt_name == "stories" else h - 110
    draw_rounded_rect(draw, (margin, cta_y, w - margin, cta_y + 56), 8, COLORS["cta"])
    cta_text = "Ver planos"
    bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
    cta_tw = bbox[2] - bbox[0]
    draw.text(((w - cta_tw) // 2, cta_y + 12), cta_text, font=font_cta, fill="#ffffff")

    # URL footer
    draw.text((margin, cta_y + 70), "app.boopixel.com/pricing", font=font_url, fill=COLORS["text_soft"])

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
