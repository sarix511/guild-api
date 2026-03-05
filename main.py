from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageFont
import requests, io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

TEXT_AREA = {"x": 220, "y": 1060, "width": 715, "height": 75}

@app.get("/generate")
async def generate(guild_name: str = Query(...)):
    try:
        # Background image
        img_url = "https://cdn.designfast.io/image/2026-03-05/8bb255db-96bc-4566-bdf4-d83815067a96.jpeg"
        resp = requests.get(img_url)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Load Google font from URL
        font_size = 70
        font_url = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"
        font_resp = requests.get(font_url)
        font = ImageFont.truetype(io.BytesIO(font_resp.content), font_size)

        # Auto-shrink font if too tall
        max_height = TEXT_AREA["height"]
        bbox = draw.textbbox((0,0), guild_name, font=font)
        text_height = bbox[3] - bbox[1]
        while text_height > max_height and font_size > 10:
            font_size -= 2
            font = ImageFont.truetype(io.BytesIO(font_resp.content), font_size)
            bbox = draw.textbbox((0,0), guild_name, font=font)
            text_height = bbox[3] - bbox[1]

        text_width = bbox[2] - bbox[0]

        # Bottom-aligned + horizontal center
        x = TEXT_AREA["x"] + (TEXT_AREA["width"] - text_width)//2
        y = TEXT_AREA["y"] + TEXT_AREA["height"] - text_height

        # Outline
        outline_range = 3
        for ox in range(-outline_range, outline_range+1):
            for oy in range(-outline_range, outline_range+1):
                draw.text((x+ox, y+oy), guild_name, font=font, fill="black")

        # White text
        draw.text((x, y), guild_name, font=font, fill="white")

        # Return image
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return StreamingResponse(img_bytes, media_type="image/png")

    except Exception as e:
        return {"error": str(e)}
