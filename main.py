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

BLANK_AREA = {
    "x": 260,
    "y": 930,
    "width": 650,
    "height": 80
}

@app.get("/generate")
async def generate(guild_name: str = Query(...), guild_id: str = Query(...)):
    try:
        # Background image
        img_url = "https://cdn.designfast.io/image/2026-03-05/8bb255db-96bc-4566-bdf4-d83815067a96.jpeg"
        resp = requests.get(img_url)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Start with max font size (rectangle height minus outline)
        max_font_size = BLANK_AREA["height"] - 10  # leave space for outline
        font_path = "fonts/arial.ttf"

        # Try to fit text width as well
        font_size = max_font_size
        while font_size > 10:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
            
            bbox = draw.textbbox((0,0), guild_name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            if text_width <= BLANK_AREA["width"] and text_height <= BLANK_AREA["height"]:
                break
            font_size -= 1

        # Center text
        x = BLANK_AREA["x"] + (BLANK_AREA["width"] - text_width) // 2
        y = BLANK_AREA["y"] + (BLANK_AREA["height"] - text_height) // 2

        # Outline
        outline_range = 3
        for ox in range(-outline_range, outline_range+1):
            for oy in range(-outline_range, outline_range+1):
                draw.text((x+ox, y+oy), guild_name, font=font, fill="black")

        # White text
        draw.text((x, y), guild_name, font=font, fill="white")

        # Return PNG
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return StreamingResponse(img_bytes, media_type="image/png")

    except Exception as e:
        return {"error": str(e)}
