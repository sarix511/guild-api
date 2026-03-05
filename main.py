from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageFont
import requests
import io

app = FastAPI()

# Allow all origins (safe for image API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background image (your provided image)
BACKGROUND_URL = "https://cdn.designfast.io/image/2026-03-05/8bb255db-96bc-4566-bdf4-d83815067a96.jpeg"

# Text rectangle
TEXT_AREA = {
    "x": 220,
    "y": 1060,
    "width": 715,
    "height": 75
}

@app.get("/generate")
async def generate(guild_name: str = Query(...)):
    try:
        # Download background image
        response = requests.get(BACKGROUND_URL)
        response.raise_for_status()

        image = Image.open(io.BytesIO(response.content)).convert("RGBA")
        draw = ImageDraw.Draw(image)

        # Load local font
        font_path = "fonts/Roboto-Regular.ttf"
        font_size = 70
        font = ImageFont.truetype(font_path, font_size)

        # Auto shrink if text height exceeds rectangle height
        max_height = TEXT_AREA["height"]

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

        # Bottom align vertically
        y = TEXT_AREA["y"] + TEXT_AREA["height"] - text_height

        # Draw outline
        outline_range = 3
        for ox in range(-outline_range, outline_range + 1):
            for oy in range(-outline_range, outline_range + 1):
                draw.text((x + ox, y + oy), guild_name, font=font, fill="black")

        # Draw main white text
        draw.text((x, y), guild_name, font=font, fill="white")

        # Return image
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        return StreamingResponse(img_bytes, media_type="image/png")

    except Exception as e:
        return {"error": str(e)}
