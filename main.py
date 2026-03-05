from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw, ImageFont
import requests, io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/generate")
async def generate(guild_name: str = Query(..., description="Name of the Guild")):
    # Background image
    image_url = "https://cdn.designfast.io/image/2026-03-05/8bb255db-96bc-4566-bdf4-d83815067a96.jpeg"
    resp = requests.get(image_url)
    img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Font
    try:
        font = ImageFont.truetype("fonts/arial.ttf", 60)
    except:
        font = ImageFont.load_default()

    # Text position
    x, y = 250, 200

    # Black outline
    outline_range = 2
    for ox in range(-outline_range, outline_range+1):
        for oy in range(-outline_range, outline_range+1):
            draw.text((x+ox, y+oy), guild_name, font=font, fill="black")

    # White text
    draw.text((x, y), guild_name, font=font, fill="white")

    # Save to BytesIO
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return StreamingResponse(img_bytes, media_type="image/png")