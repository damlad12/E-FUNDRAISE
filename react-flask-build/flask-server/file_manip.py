
import openai
import time
import sys
import fitz  # PyMuPDF
import tiktoken
import os

sys.stdout.reconfigure(encoding='utf-8')
# Function to extract text from a list of PDF files

def extract_text_from_pdfs(pdf_paths):
    extracted_texts = []
    
    for pdf_path in pdf_paths:
        text = ""
        try:
            with fitz.open(pdf_path) as pdf_document:
                for page_number in range(pdf_document.page_count):
                    page = pdf_document.load_page(page_number)
                    text += page.get_text() + "\n"  # Add newline for readability between pages
        except Exception as e:
            print(f"Error reading {pdf_path}: {str(e)}")
            continue
        
        extracted_texts.append(text)
    
    return extracted_texts

def split_text_into_chunks(text, max_tokens=2000):
    # Use a tokenizer compatible with GPT-3.5 and GPT-4
    tokenizer = tiktoken.get_encoding("cl100k_base")
    
    tokens = tokenizer.encode(text)
    chunks = []

    # Split tokens into chunks of max_tokens size
    for i in range(0, len(tokens), max_tokens):
        chunk = tokens[i:i + max_tokens]
        chunks.append(tokenizer.decode(chunk))
    
    return chunks

def is_folder_empty(folder_path):
    # List all items in the folder
    return len(os.listdir(folder_path)) == 0

