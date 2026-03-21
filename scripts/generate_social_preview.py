from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT = BASE_DIR / "docs" / "assets" / "12-social-preview.png"

WIDTH = 1280
HEIGHT = 640


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(path, size=size)
    except OSError:
        return ImageFont.load_default()


def rounded_rectangle(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def draw_chip(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font, fill, text_fill) -> int:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    width = right - left + 32
    height = bottom - top + 18
    rounded_rectangle(draw, (x, y, x + width, y + height), radius=20, fill=fill)
    draw.text((x + 16, y + 8), text, font=font, fill=text_fill)
    return width


def main() -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#f7efe6")
    draw = ImageDraw.Draw(image, "RGBA")

    # Background glows
    draw.ellipse((-120, -80, 340, 360), fill=(210, 114, 67, 90))
    draw.ellipse((930, -60, 1390, 380), fill=(20, 95, 102, 85))
    draw.ellipse((820, 360, 1380, 860), fill=(20, 95, 102, 60))

    # Main card
    rounded_rectangle(draw, (60, 56, 1220, 584), radius=42, fill=(255, 250, 244, 235))
    rounded_rectangle(draw, (94, 94, 1186, 546), radius=30, fill=(255, 255, 255, 105))

    title_font = load_font(r"C:\Windows\Fonts\msyhbd.ttc", 64)
    subtitle_font = load_font(r"C:\Windows\Fonts\msyh.ttc", 28)
    body_font = load_font(r"C:\Windows\Fonts\msyh.ttc", 26)
    chip_font = load_font(r"C:\Windows\Fonts\seguisb.ttf", 24)
    small_font = load_font(r"C:\Windows\Fonts\seguisb.ttf", 22)

    draw.text((118, 116), "Zhiyuxing AI Assistant", font=title_font, fill="#193241")
    draw.text(
        (122, 198),
        "AI emotional support and study assistance for student scenarios",
        font=subtitle_font,
        fill="#4d6170",
    )
    draw.text(
        (122, 244),
        "面向大学生场景的 AI 情绪支持与学习辅助服务",
        font=subtitle_font,
        fill="#4d6170",
    )

    chip_y = 312
    chip_x = 122
    chip_gap = 14
    for text, fill, text_fill in [
        ("FastAPI Web", (20, 95, 102, 220), "#fdfbf8"),
        ("Local Demo Mode", (210, 114, 67, 220), "#fff8f4"),
        ("OpenAI & DeepSeek", (29, 41, 53, 205), "#f5f6f8"),
    ]:
        width = draw_chip(draw, chip_x, chip_y, text, chip_font, fill, text_fill)
        chip_x += width + chip_gap

    lines = [
        "• Runnable web UI with bilingual docs and CI",
        "• One-click provider setup + compatibility preflight checks",
        "• Designed for academic pressure, procrastination, exam and interview stress",
    ]
    y = 392
    for line in lines:
        draw.text((124, y), line, font=body_font, fill="#23414f")
        y += 48

    # Right-side stat cards
    cards = [
        ("Run Fast", "No API key is needed for demo mode"),
        ("Integrate Real Models", "OpenAI-compatible and DeepSeek presets"),
        ("Use in Portfolio", "Clear docs, screenshots, tests, and releases"),
    ]
    card_y = 132
    for title, desc in cards:
        rounded_rectangle(draw, (850, card_y, 1138, card_y + 104), radius=24, fill=(255, 255, 255, 190))
        draw.text((874, card_y + 18), title, font=small_font, fill="#155c63")
        draw.text((874, card_y + 52), desc, font=load_font(r"C:\Windows\Fonts\msyh.ttc", 18), fill="#52636f")
        card_y += 122

    draw.text(
        (874, 504),
        "github.com/1420079678-ctrl",
        font=load_font(r"C:\Windows\Fonts\seguisb.ttf", 18),
        fill="#23414f",
    )
    draw.text(
        (874, 528),
        "/zhiyuxing-ai-assistant",
        font=load_font(r"C:\Windows\Fonts\seguisb.ttf", 18),
        fill="#23414f",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)
    print(f"saved: {OUTPUT}")


if __name__ == "__main__":
    main()
