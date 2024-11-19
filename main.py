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
def load_text_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


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
) -> FileResponse:
    """
    Processes uploaded text and image files to generate a word cloud.

    This endpoint accepts a text file, an image file, and a mask color as input.
    It uses the text file's content to generate a word cloud, which is shaped
    according to the provided image and masked using the selected color. The
    generated word cloud is returned as a PNG image.

    ### Parameters:
    - `text_file` (UploadFile):
        A `.txt` file containing text to analyze. Stopwords will be
        automatically removed.
    - `image_file` (UploadFile):
        A `.png` file used as the mask for shaping the word cloud.
    - `mask_color` (str):
        A hexadecimal color value (e.g., `#ffffff`) representing the color to be
        masked in the image. All parts of the image matching this color will
        define the area of the word cloud.

    ### Returns:
    - `FileResponse`: A PNG image of the generated word cloud.

    ### Notes:
    - The uploaded files are saved temporarily for processing and then deleted.

    ### Example Request (via FormData):
    ```
    POST /process/
    Content-Type: multipart/form-data
    {
        "text_file": <uploaded .txt file>,
        "image_file": <uploaded .png file>,
        "mask_color": "#ffffff"
    }
    ```

    ### Example Response:
    - A PNG file containing the generated word cloud.

    """
    text_path = "temp_text.txt"
    image_path = "temp_image.png"
    await save_uploaded_file(text_file, text_path)
    await save_uploaded_file(image_file, image_path)

    mask_image, color_image = prepare_mask_image(image_path, mask_color)

    wc = generate_wordcloud(
        all_words=load_text_file(text_path),
        mask_image=mask_image,
        stopwords=get_stopwords(),
        color_image=color_image,
    )

    output_path = "output_wordcloud.png"
    wc.to_file(output_path)

    clean_up_files(text_path, image_path)

    return FileResponse(output_path, media_type="image/png")
