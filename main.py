from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageFont
import requests, io

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/generate")
async def generate(guild_name: str = Query(...)):
    try:
        # Background image
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

        # Dynamic font size using draw.textbbox
        max_font_size = 250
        while True:
            if isinstance(font, ImageFont.FreeTypeFont):
                bbox = draw.textbbox((0,0), guild_name, font=font)
                text_width = bbox[2] - bbox[0]
            else:
                text_width, _ = draw.textsize(guild_name, font=font)
            
            if text_width >= max_width or font_size >= max_font_size:
                break
            
            font_size += 5
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                break

        # Position (adjust vertical)
        if isinstance(font, ImageFont.FreeTypeFont):
            bbox = draw.textbbox((0,0), guild_name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width, text_height = draw.textsize(guild_name, font=font)

        x = (img.width - text_width) // 2
        y = 180  # adjust vertical position to blank area

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
