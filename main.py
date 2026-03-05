from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageFont
import requests, io, base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Rectangle for guild name
BLANK_AREA = {"x": 260, "y": 930, "width": 650, "height": 80}

# Base64-encoded font (Arial example) – replace with actual base64 of arial.ttf
FONT_B64 = """
AAEAAAASAQAABAAgR0RFRrRCsIIAA...
"""  # Truncated, use full base64 of arial.ttf

def get_font(size: int):
    try:
        font_bytes = io.BytesIO(base64.b64decode(FONT_B64))
        font = ImageFont.truetype(font_bytes, size)
    except:
        font = ImageFont.load_default()
    return font

@app.get("/generate")
async def generate(guild_name: str = Query(...)):
    try:
        # Background image
        img_url = "https://cdn.designfast.io/image/2026-03-05/8bb255db-96bc-4566-bdf4-d83815067a96.jpeg"
        resp = requests.get(img_url)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Fixed font size
        font_size = 70
        font = get_font(font_size)

        # Text size
        bbox = draw.textbbox((0,0), guild_name, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center in rectangle
        x = BLANK_AREA["x"] + (BLANK_AREA["width"] - text_width)//2
        y = BLANK_AREA["y"] + (BLANK_AREA["height"] - text_height)//2

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
