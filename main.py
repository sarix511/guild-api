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
async def generate(guild_name: str = Query(...), guild_id: str = Query(...)):
    try:
        # Background image
        img_url = "https://cdn.designfast.io/image/2026-03-05/8bb255db-96bc-4566-bdf4-d83815067a96.jpeg"
        resp = requests.get(img_url)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Font
        font_size = 70  # Fixed large size
        font_path = "fonts/arial.ttf"
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        # Position
        # Adjust x, y according to blank space above guild ID
        x = 250  # horizontal start (adjust to center)
        y = 150  # vertical position above guild ID (adjust)

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
