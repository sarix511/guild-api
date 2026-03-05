from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background Image (Postimg)
BACKGROUND_URL = "https://i.postimg.cc/j2wKc17D/background.jpg"

# Text rectangle
TEXT_AREA = {
    "x": 220,
    "y": 1060,
    "width": 715,
    "height": 75
}

@app.get("/")
def home():
    return {"status": "API is running"}

@app.get("/generate")
async def generate(guild_name: str = Query(...)):
    try:
        # Download image safely
        response = requests.get(
            BACKGROUND_URL,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        response.raise_for_status()

        # Verify image before opening
        image_bytes = io.BytesIO(response.content)
        try:
            image = Image.open(image_bytes)
            image.verify()
        except:
            return {"error": "Invalid image format from host."}

        # Reopen image after verify
        image_bytes.seek(0)
        image = Image.open(image_bytes).convert("RGBA")
        draw = ImageDraw.Draw(image)

        # Load font (absolute path)
        font_path = os.path.join(
            os.path.dirname(__file__),
            "fonts",
            "Roboto-Regular.ttf"
        )

        if not os.path.exists(font_path):
            return {"error": "Font file not found."}

        font_size = 70
        font = ImageFont.truetype(font_path, font_size)

        max_height = TEXT_AREA["height"]

        # Auto shrink if needed
        while True:
            bbox = draw.textbbox((0, 0), guild_name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            if text_height <= max_height or font_size <= 15:
                break

            font_size -= 2
            font = ImageFont.truetype(font_path, font_size)

        # Center horizontally
        x = TEXT_AREA["x"] + (TEXT_AREA["width"] - text_width) // 2

        # Bottom align
        y = TEXT_AREA["y"] + TEXT_AREA["height"] - text_height

        # Outline
        outline_range = 3
        for ox in range(-outline_range, outline_range + 1):
            for oy in range(-outline_range, outline_range + 1):
                draw.text((x + ox, y + oy), guild_name, font=font, fill="black")

        # White text
        draw.text((x, y), guild_name, font=font, fill="white")

        # Return PNG
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        return StreamingResponse(img_bytes, media_type="image/png")

    except Exception as e:
        return {"error": str(e)}
