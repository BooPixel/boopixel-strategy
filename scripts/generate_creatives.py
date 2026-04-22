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
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from sqlalchemy import create_engine, text

load_dotenv(os.path.expanduser("~/.env"))

ENGINE = create_engine(os.environ["DATABASE_URL"])

BG_IMAGE_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "business-frontend",
    "public",
    "footer-boopixel.png",
)
# Fallback: look relative to script dir
if not os.path.exists(BG_IMAGE_PATH):
    BG_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "assets", "footer-boopixel.png")

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

    # Background with footer image + dark gradient overlay
    img = Image.new("RGBA", (w, h), COLORS["bg"])

    if os.path.exists(BG_IMAGE_PATH):
        bg = Image.open(BG_IMAGE_PATH).convert("RGBA")
        # Scale to fill width, position at bottom
        bg_ratio = w / bg.width
        bg_resized = bg.resize((w, int(bg.height * bg_ratio)))
        # Place at bottom of image
        bg_y = h - bg_resized.height
        if bg_y < 0:
            bg_resized = bg_resized.crop((0, -bg_y, w, bg_resized.height))
            bg_y = 0
        img.paste(bg_resized, (0, bg_y))

        # Dark gradient overlay: solid dark top fading to semi-transparent bottom
        gradient = Image.new("RGBA", (w, h), "#00000000")
        gdraw = ImageDraw.Draw(gradient)
        # Top 60% = solid dark bg
        solid_end = int(h * 0.55)
        bg_rgb = tuple(int(COLORS["bg"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        for y_pos in range(solid_end):
            gdraw.line([(0, y_pos), (w, y_pos)], fill=(*bg_rgb, 255))
        # 55%-85% = fade from solid to semi-transparent
        fade_start = solid_end
        fade_end = int(h * 0.85)
        for y_pos in range(fade_start, fade_end):
            progress = (y_pos - fade_start) / (fade_end - fade_start)
            alpha = int(255 * (1 - progress * 0.6))
            gdraw.line([(0, y_pos), (w, y_pos)], fill=(*bg_rgb, alpha))
        # 85%-100% = semi-transparent (image shows through)
        for y_pos in range(fade_end, h):
            gdraw.line([(0, y_pos), (w, y_pos)], fill=(*bg_rgb, 100))

        img = Image.alpha_composite(img, gradient)

    draw = ImageDraw.Draw(img)

    # Scale factor: all sizes proportional to width (base = 1080)
    s = w / 1080

    font_brand = get_font(int(36 * s))
    font_category = get_font(int(26 * s))
    font_name = get_font(int(82 * s), bold=True)
    font_price = get_font(int(64 * s), bold=True)
    font_yearly = get_font(int(28 * s))
    font_item = get_font(int(32 * s))
    font_item_note = get_font(int(26 * s))
    font_cta = get_font(int(38 * s), bold=True)
    font_url = get_font(int(26 * s))

    margin = int(90 * s)
    y = int(70 * s) if fmt_name == "feed" else int(200 * s)

    # Brand name
    draw.text((margin, y), "BOOPIXEL", font=font_brand, fill=COLORS["accent_light"])
    y += int(60 * s)

    # Category badge pill
    cat_label = CATEGORY_LABELS.get(category, category or "").upper()
    if cat_label:
        bbox = draw.textbbox((0, 0), cat_label, font=font_category)
        cat_w = bbox[2] - bbox[0] + int(30 * s)
        cat_h = int(38 * s)
        badge_color = COLORS["badge_addon"] if is_addon else COLORS["border"]
        draw_rounded_rect(draw, (margin, y, margin + cat_w, y + cat_h), int(19 * s), badge_color)
        draw.text((margin + int(15 * s), y + int(5 * s)), cat_label, font=font_category, fill=COLORS["text"])
        y += int(56 * s)

    # Plan name
    draw.text((margin, y), name, font=font_name, fill=COLORS["text"])
    y += int(105 * s)

    # Featured badge
    if featured:
        feat_w = int(240 * s)
        feat_h = int(40 * s)
        draw_rounded_rect(draw, (margin, y, margin + feat_w, y + feat_h), int(20 * s), COLORS["accent"])
        draw.text((margin + int(18 * s), y + int(5 * s)), "MAIS POPULAR", font=font_category, fill=COLORS["text"])
        y += int(58 * s)

    # Price
    price_text = f"{format_price(monthly)}/mes"
    draw.text((margin, y), price_text, font=font_price, fill=COLORS["price"])
    y += int(78 * s)

    # Yearly price
    yearly_text = f"ou {format_price(yearly)}/ano"
    draw.text((margin, y), yearly_text, font=font_yearly, fill=COLORS["text_soft"])
    y += int(54 * s)

    # Divider line
    draw.line([(margin, y), (w - margin, y)], fill=COLORS["border"], width=max(1, int(2 * s)))
    y += int(30 * s)

    # Items list
    check_offset = int(40 * s)
    if items_raw:
        items = items_raw.split("|")
        max_items = 5 if fmt_name == "feed" else 9
        for item in items[:max_items]:
            parts = item.split(" — ")
            item_name = parts[0].strip() if parts else item
            item_note = parts[1].strip() if len(parts) > 1 else ""

            check_color = COLORS["price"] if not is_addon else COLORS["badge_addon"]
            draw.text((margin + int(5 * s), y), "\u2713", font=font_item, fill=check_color)
            draw.text((margin + check_offset, y), item_name, font=font_item, fill=COLORS["text"])
            y += int(38 * s)
            if item_note:
                draw.text((margin + check_offset, y), item_note, font=font_item_note, fill=COLORS["text_muted"])
                y += int(32 * s)
            y += int(10 * s)

        if len(items) > max_items:
            remaining = len(items) - max_items
            draw.text((margin + check_offset, y), f"+ {remaining} mais...", font=font_item_note, fill=COLORS["accent_light"])
            y += int(42 * s)

    # CTA button
    cta_h = int(64 * s)
    cta_y = h - int(150 * s) if fmt_name == "stories" else h - int(130 * s)
    draw_rounded_rect(draw, (margin, cta_y, w - margin, cta_y + cta_h), int(10 * s), COLORS["cta"])
    cta_text = "Ver planos"
    bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
    cta_tw = bbox[2] - bbox[0]
    cta_th = bbox[3] - bbox[1]
    draw.text(((w - cta_tw) // 2, cta_y + (cta_h - cta_th) // 2), cta_text, font=font_cta, fill="#ffffff")

    # URL footer
    draw.text((margin, cta_y + cta_h + int(16 * s)), "app.boopixel.com/pricing", font=font_url, fill=COLORS["text_soft"])

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
