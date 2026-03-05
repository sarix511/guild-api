from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = FastAPI()

# CORS allow
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Text rectangle (reference)
TEXT_AREA = {
    "x": 220,
    "y": 1060,
    "width": 715,
    "height": 75
}

# Shifts
VERTICAL_SHIFT_UP = -380   # 10 cm below
HORIZONTAL_SHIFT = 150     # 4 cm right

@app.get("/")
def home():
    return {"status": "API is running"}

@app.get("/generate")
async def generate(guild_name: str = Query(...)):
    try:
        # Load background
        image_path = os.path.join(os.path.dirname(__file__), "background.jpg")
        if not os.path.exists(image_path):
            return {"error": "Background image not found."}

        image = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(image)

        # Load font
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "Roboto-Regular.ttf")
        if not os.path.exists(font_path):
            return {"error": "Font file not found."}

        font_size = 90
        font = ImageFont.truetype(font_path, font_size)
        max_height = TEXT_AREA["height"]

        # Auto shrink if too tall
        while True:
            bbox = draw.textbbox((0, 0), guild_name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            if text_height <= max_height or font_size <= 15:
                break
            font_size -= 2
            font = ImageFont.truetype(font_path, font_size)

        # Horizontal center + 4cm right
        x = TEXT_AREA["x"] + (TEXT_AREA["width"] - text_width) // 2 + HORIZONTAL_SHIFT

        # Vertical: bottom align + 10cm below
        y = TEXT_AREA["y"] + TEXT_AREA["height"] - text_height - VERTICAL_SHIFT_UP

        # Draw outline
        outline_range = 3
        for ox in range(-outline_range, outline_range + 1):
            for oy in range(-outline_range, outline_range + 1):
                draw.text((x + ox, y + oy), guild_name, font=font, fill="black")

        # Draw main text
        draw.text((x, y), guild_name, font=font, fill="white")

        # Return image
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return StreamingResponse(img_bytes, media_type="image/png")

    except Exception as e:
        return {"error": str(e)}
