import openai
import pytesseract
from PIL import Image
import base64
import re
import logging

# Configure
openai.api_key = "api-key"  
logging.basicConfig(level=logging.INFO)

# "printed", "handwritten", or "not sure"
file_type = "printed"
image_path = "path/to/image.jpg"  # actual image path

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def is_satisfactory(text):
    # Very basic checks 
    has_date = bool(re.search(r"\d{2}/\d{2}/\d{4}", text))
    has_amount = bool(re.search(r"\$?\d+[.,]?\d*\s?(USD|KZT|EUR)?", text))
    has_name = bool(re.search(r"[A-Z][a-z]+ [A-Z][a-z]+", text))
    return has_date and has_amount and has_name

def use_openai_vision(image_path):
    try:
        logging.info("Fallback: Using OpenAI Vision API...")
        base64_image = image_to_base64(image_path)

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all text from this fine, especially name, date, and amount."},
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

# Run
if __name__ == "__main__":
    final_result = process_document(file_type, image_path)
    print("\nFinal Result:\n")
    print(final_result)
