import streamlit as st
import requests

st.title("📄 PDF OCR Extractor")
st.write("Upload a PDF file and choose how to extract text from it.")

# Upload PDF file
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

# Choose OCR type
ocr_type = st.selectbox("Select OCR Type", ["printed", "handwritten"])

# When user clicks "Process"
if uploaded_file and st.button("Process PDF"):
    with st.spinner("Processing..."):
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        data = {"file_type": ocr_type}

        try:
            response = requests.post("http://127.0.0.1:8000/ocr/", files=files, data=data)
            if response.status_code == 200:
                st.subheader("📃 Extracted Text")
                st.text_area("OCR Result", value=response.text, height=500)
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
