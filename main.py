from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from wordcloud import WordCloud, ImageColorGenerator
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


# Function to save the uploaded file to disk
async def save_uploaded_file(upload_file: UploadFile, file_path: str):
    with open(file_path, "wb") as f:
        f.write(await upload_file.read())


# Function to load the text file and convert it into a pandas DataFrame
def load_text_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
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
    return pd.DataFrame(data)


# Function to load stopwords from the file
def get_stopwords():
    with open("stopwords-en.txt", "r", encoding="utf-8") as f:
        return f.read().split("\n")


# Function to process the uploaded image and create the mask
def prepare_mask_image(image_path: str, mask_color: str):
    color_image = np.array(Image.open(image_path).convert("RGB"))
    mask_image = color_image.copy()
    mask_color_rgb = tuple(
        int(mask_color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)
    )
    mask_pixels = np.all(color_image == mask_color_rgb, axis=-1)
    mask_image[mask_pixels] = 255
    mask_image[~mask_pixels] = 0
    return mask_image, color_image


# Function to generate the word cloud from the text and mask
def generate_wordcloud(all_words: str, mask_image, stopwords, color_image):
    wc = WordCloud(
        mask=mask_image,
        contour_width=5,
        contour_color="black",
        min_font_size=8,
        stopwords=stopwords,
        collocations=False,
    ).generate(all_words)
    wc.recolor(color_func=ImageColorGenerator(color_image))
    return wc


# Function to clean up temporary files
def clean_up_files(*file_paths):
    for file_path in file_paths:
        os.remove(file_path)


@app.post("/process/")
async def process_files(
    text_file: UploadFile,
    image_file: UploadFile,
    mask_color: str = Form(...),
):
    # Define file paths for temporary storage
    text_path = "temp_text.txt"
    image_path = "temp_image.png"

    # Save the uploaded files
    await save_uploaded_file(text_file, text_path)
    await save_uploaded_file(image_file, image_path)

    # Load and process text file
    df = load_text_file(text_path)
    all_words = " ".join(df["text"].to_list()).lower()

    # Get stopwords
    stopwords = get_stopwords()

    # Prepare the mask image
    mask_image, color_image = prepare_mask_image(image_path, mask_color)

    # Generate the word cloud
    wc = generate_wordcloud(all_words, mask_image, stopwords, color_image)

    # Save the generated word cloud to a file
    output_path = "output_wordcloud.png"
    wc.to_file(output_path)

    # Clean up temporary files
    clean_up_files(text_path, image_path)

    return FileResponse(output_path, media_type="image/png")
