from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from wordcloud import WordCloud, ImageColorGenerator
from datetime import datetime, date
from PIL import Image
import pandas as pd
import numpy as np
import os

app = FastAPI()

# Serve static files (e.g., CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_homepage():
    with open("index.html", "r") as f:
        return f.read()


@app.post("/process/")
async def process_files(
    text_file: UploadFile,
    image_file: UploadFile,
    mask_color: str = Form(...),
):
    # Save uploaded files temporarily
    text_path = "temp_text.txt"
    image_path = "temp_image.png"

    with open(text_path, "wb") as f:
        f.write(await text_file.read())
    with open(image_path, "wb") as f:
        f.write(await image_file.read())

    # Load transcript data
    with open(text_path, "r", encoding="utf-8") as f:
        raw_data = f.read()
    lines = raw_data.split("\n")
    data = []
    for i in range(0, len(lines), 3):
        data.append(
            {
                "ts": lines[i],
                "speaker": lines[i + 1],
                "text": lines[i + 2],
            }
        )
    df = pd.DataFrame(data)

    # Extract word counts
    with open("stopwords-en.txt", "r", encoding="utf-8") as f:
        stopwords = f.read().split("\n")
    all_words = " ".join(df["text"].to_list()).lower()

    # Convert hex color to RGB
    mask_color_rgb = tuple(
        int(mask_color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)
    )

    # Process the image
    color_image = np.array(Image.open(image_path).convert("RGB"))
    mask_image = color_image.copy()

    # Create the mask based on the selected mask color
    mask_pixels = np.all(color_image == mask_color_rgb, axis=-1)
    mask_image[~mask_pixels] = 0

    wc = WordCloud(
        mask=mask_image,
        contour_width=5,
        contour_color="black",
        min_font_size=8,
        stopwords=stopwords,
        collocations=False,
    ).generate(all_words)
    wc.recolor(color_func=ImageColorGenerator(color_image))

    output_path = "output_wordcloud.png"
    wc.to_file(output_path)

    # Clean up temporary files
    os.remove(text_path)
    os.remove(image_path)

    return FileResponse(output_path, media_type="image/png")
