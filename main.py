from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageFont
import requests, io

app = FastAPI()

# Allow all origins for browser / JS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/generate")
async def generate(guild_name: str = Query(...)):
    try:
        # Real background image
        img_url = "https://cdn.designfast.io/image/2026-03-05/8bb255db-96bc-4566-bdf4-d83815067a96.jpeg"
        resp = requests.get(img_url)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Font
        font_path = "fonts/arial.ttf"
        font_size = 10
        max_width = img.width - 100

        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        # Dynamic font size
        max_font_size = 250
        if isinstance(font, ImageFont.FreeTypeFont):
            while font.getsize(guild_name)[0] < max_width and font_size < max_font_size:
                font_size += 5
                font = ImageFont.truetype(font_path, font_size)

        # Text position (adjust to blank area)
        text_width, text_height = draw.textsize(guild_name, font=font)
        x = (img.width - text_width) // 2
        y = 180  # adjust vertical position according to blank space

        # Black outline
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
