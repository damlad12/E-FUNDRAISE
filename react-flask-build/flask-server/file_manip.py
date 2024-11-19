
import openai
import time
import sys
import fitz  # PyMuPDF
import tiktoken
import os
import logging

sys.stdout.reconfigure(encoding='utf-8')
# Function to extract text from a list of PDF files
logging.basicConfig(filename="pdf_extraction_errors.log", level=logging.ERROR, format='%(asctime)s %(message)s')

def extract_text_from_pdfs_in_folder(folder_path):
    extracted_texts = []

    # Get a list of all PDF files in the folder
    pdf_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

    for pdf_path in pdf_paths:
        text = ""
        try:
            with fitz.open(pdf_path) as pdf_document:
                for page_number in range(pdf_document.page_count):
                    try:
                        page = pdf_document.load_page(page_number)
                        text += page.get_text() + "\n"  # Add newline for readability between pages
                    except Exception as e:
                        logging.error(f"Error reading page {page_number} of {pdf_path}: {str(e)}")
                        continue
        except Exception as e:
            logging.error(f"Error reading {pdf_path}: {str(e)}")
            continue
        
        extracted_texts.append({"file": pdf_path, "content": text})
    
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

