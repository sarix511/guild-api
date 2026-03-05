from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rectangle for text
TEXT_AREA = {
    "x": 220,
    "y": 1060,    # adjust if needed
    "width": 715,
    "height": 75
}

@app.get("/")
def home():
    return {"status": "API is running"}

@app.get("/generate")
async def generate(guild_name: str = Query(...)):
    try:
        # Load local background
        image_path = os.path.join(os.path.dirname(__file__), "background.jpg")
        if not os.path.exists(image_path):
            return {"error": "Background image not found."}

        image = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(image)

        # Load font
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "Roboto-Regular.ttf")
        if not os.path.exists(font_path):
            return {"error": "Font file not found."}

        font_size = 70
        font = ImageFont.truetype(font_path, font_size)
        max_height = TEXT_AREA["height"]

        # Auto shrink font if too tall
        while True:
            bbox = draw.textbbox((0,0), guild_name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            if text_height <= max_height or font_size <= 15:
                break
            font_size -= 2
            font = ImageFont.truetype(font_path, font_size)

        # Horizontal center
        x = TEXT_AREA["x"] + (TEXT_AREA["width"] - text_width) // 2

        # Vertical: bottom align in rectangle, then shift UP to appear above UID
        vertical_shift_up = 20  # tweak this to adjust how high above UID
        y = TEXT_AREA["y"] + TEXT_AREA["height"] - text_height - vertical_shift_up

        # Draw outline
        outline_range = 3
        for ox in range(-outline_range, outline_range+1):
            for oy in range(-outline_range, outline_range+1):
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
