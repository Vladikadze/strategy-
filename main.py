import os
import base64
import logging
import tempfile
import re

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import PlainTextResponse
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import openai


# Configure
openai.api_key = ""
logging.basicConfig(level=logging.INFO)

app = FastAPI()

with open("output.txt", "w") as file:
    file.write("Document OCR Results:\n\n")

# Save each page as image
for i, image in enumerate(images):
    image.save(f"page_{i + 1}.png", "PNG")
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def is_satisfactory(text):
    # Very basic checks 
    #has_date = bool(re.search(r"\d{2}/\d{2}/\d{4}", text))
    #has_amount = bool(re.search(r"\$?\d+[.,]?\d*\s?(USD|KZT|EUR)?", text))
    #has_name = bool(re.search(r"[A-Z][a-z]+ [A-Z][a-z]+", text))
    #return has_date and has_amount and has_name
    return True

def use_openai_vision(image_path):
    try:
        logging.info("Fallback: Using OpenAI Vision API...")
        base64_image = image_to_base64(image_path)

        response = openai.chat.completions.create(
            model="gpt-4o",  # updated model name
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all text from this file."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            max_tokens=1000
        )

        result = response.choices[0].message.content
        return result
    except Exception as e:
        logging.error(f"OpenAI Vision error: {e}")
        return ""

def use_local_ocr(image_path):
    try:
        logging.info("Using local Tesseract OCR...")
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logging.error(f"Local OCR error: {e}")
        return ""

def process_document(file_type, image_path):
    if file_type == "handwritten":
        result = use_openai_vision(image_path)
        return result if is_satisfactory(result) else "OpenAI Vision failed"
    else:  # printed or not sure
        result = use_local_ocr(image_path)
        if is_satisfactory(result):
            return f"Local OCR succeeded:\n\n{result}"
        result = use_openai_vision(image_path)
        if is_satisfactory(result):
            return f"Fallback (OpenAI Vision) succeeded:\n\n{result}"
        return "Both OCR methods failed or gave unsatisfactory results."

@app.post("/ocr/", response_class=PlainTextResponse)
async def upload_pdf(file: UploadFile = File(...), file_type: str = Form("printed")):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save uploaded PDF
        pdf_path = os.path.join(tmpdir, "uploaded.pdf")
        with open(pdf_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Convert PDF to images
        images = convert_from_path(pdf_path)
        results = ["Document OCR Results:\n"]

        for i, image in enumerate(images):
            image_path = os.path.join(tmpdir, f"page_{i + 1}.png")
            image.save(image_path, "PNG")
            logging.info(f"Processing image: {image_path}")
            result = process_document(file_type, image_path)
            results.append(f"\nPage {i+1}:\n{result}")

        return "\n".join(results)
