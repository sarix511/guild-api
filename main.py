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

# Blank area rectangle
BLANK_AREA = {"x": 260, "y": 930, "width": 650, "height": 80}

@app.get("/generate")
async def generate(guild_name: str = Query(...), guild_id: str = Query(...)):
    try:
        # Background image
        img_url = "https://cdn.designfast.io/image/2026-03-05/8bb255db-96bc-4566-bdf4-d83815067a96.jpeg"
        resp = requests.get(img_url)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Font
        font_path = "fonts/arial.ttf"
        max_height = BLANK_AREA["height"] - 6  # leave space for outline
        max_width = BLANK_AREA["width"] - 6
        font_size = max_height  # start with max possible height

        # Adjust font size to fit width
        while font_size > 10:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0,0), guild_name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            if text_width <= max_width and text_height <= max_height:
                break
            font_size -= 1

        # Center text in rectangle with vertical adjustment
vertical_shift = 15  # adjust this number
x = BLANK_AREA["x"] + (BLANK_AREA["width"] - text_width)//2
y = BLANK_AREA["y"] + (BLANK_AREA["height"] - text_height)//2 + vertical_shift

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
