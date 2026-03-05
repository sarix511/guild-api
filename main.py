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
async def generate(guild_name: str = Query(...)):
    # Background image
    image_url = "https://cdn.designfast.io/image/2026-03-05/8bb255db-96bc-4566-bdf4-d83815067a96.jpeg"
    resp = requests.get(image_url)
    img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Load font
    try:
        font_path = "fonts/arial.ttf"
        font_size = 10  # temporary, we will increase dynamically
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # Dynamic font size to fit width
    max_width = img.width - 100  # 50 px margin on each side
    if isinstance(font, ImageFont.FreeTypeFont):  # only for TrueType font
        while font.getsize(guild_name)[0] < max_width:
            font_size += 5
            font = ImageFont.truetype(font_path, font_size)

    # Calculate position to center text horizontally
    text_width, text_height = draw.textsize(guild_name, font=font)
    x = (img.width - text_width) // 2
    y = 200  # vertical position (adjust to blank area)

    # Black outline
    outline_range = 3
    for ox in range(-outline_range, outline_range+1):
        for oy in range(-outline_range, outline_range+1):
            draw.text((x+ox, y+oy), guild_name, font=font, fill="black")

    # White text on top
    draw.text((x, y), guild_name, font=font, fill="white")

    # Save to BytesIO
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return StreamingResponse(img_bytes, media_type="image/png")
