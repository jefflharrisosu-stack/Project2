import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import docx
from bs4 import BeautifulSoup

import os

try:
    API_KEY = st.secrets["AIzaSyC3hR7rqEoTMJUueSi5cHqbf6WN_wE1OrQ"]
except:
    st.error("API Key not found via st.secrets.")
    st.stop()

if not API_KEY:
    st.error("Missing API key.")
    st.stop()

genai.configure(api_key=API_KEY)

def get_text_from_pdf(file):
    text = ""
    pdf_reader = PdfReader(file)
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def get_text_from_docx(file):
    d = docx.Document(file)
    lines = []
    for p in d.paragraphs:
        lines.append(p.text)
    return "\n".join(lines)

def get_text_from_html(file):
    soup = BeautifulSoup(file, "html.parser")
    return soup.get_text()

def get_text_from_txt(file):
    return str(file.read(), "utf-8")

def extract_content(uploaded_file):
    file_type = uploaded_file.type
    try:
        if "pdf" in file_type:
            return get_text_from_pdf(uploaded_file)
        elif "word" in file_type or "officedocument" in file_type:
            return get_text_from_docx(uploaded_file)
        elif "html" in file_type:
            return get_text_from_html(uploaded_file)
        elif "text/plain" in file_type:
            return get_text_from_txt(uploaded_file)
        else:
            return "Error: Unsupported file type."
    except Exception as e:
        return f"Error extracting text: {e}"

st.title("Input to AI")

user_question = st.text_input("Enter your question:", placeholder="Enter your question here")

st.write("Upload attachment:")
uploaded_file = st.file_uploader(
    "Drag and drop file here",
    type=["txt", "pdf", "docx", "html"]
)

if user_question:
    model = genai.GenerativeModel("gemini-2.5-flash")

    with st.spinner("Processing..."):
        context_text = ""

        if uploaded_file is not None:
            context_text = extract_content(uploaded_file)
            if context_text.startswith("Error"):
                st.error(context_text)
                st.stop()

            prompt = (
                "Context information:\n"
                f"{context_text}\n\n"
                f"Query: {user_question}"
            )
        else:
            prompt = user_question

        try:
            response = model.generate_content(prompt)
            st.markdown("## Response:")
            st.write(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")
