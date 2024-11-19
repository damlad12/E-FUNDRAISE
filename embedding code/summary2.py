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

# Function to tokenize and split text into chunks within a token limit
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



def call_assistant_with_file(api_key,chunk):
    # Set the OpenAI API key
    openai.api_key = api_key
    
    # Create a new thread
    thread = openai.beta.threads.create()

        # Add a message from the user
    message = openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=chunk
        )

        # Create a run with the assistant
    run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id="asst_e4AK3QNJsqDWCU5tDjVioqsv"
        )

        # Retrieve the run's current state
    while True:
                run = openai.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                if run.status == "completed":
                    break
                elif run.status == "failed":
                    raise Exception("The run failed to complete successfully.")
                # Wait for a short period before polling again
                time.sleep(2)

        # Retrieve and print messages from the thread
    messages = openai.beta.threads.messages.list(
            thread_id=thread.id
        )
        
    
    return messages.data[0].content[0].text.value



if __name__ == "__main__":
    # Set your API key (ideally use environment variables for security)
    api_key = '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'  # Replace with your OpenAI API key
    # Set a list of PDF file paths
    pdf_paths = ["h.pdf"]  # Replace with actual paths

    # Extract text from all PDFs
    pdf_texts = extract_text_from_pdfs(pdf_paths)

    # Split each extracted text into chunks
    all_chunks = []
    for pdf_text in pdf_texts:
        chunks = split_text_into_chunks(pdf_text)
        all_chunks.extend(chunks)  # Combine all chunks

    # Output the chunks
    for i, chunk in enumerate(all_chunks):
        print(call_assistant_with_file(api_key,chunk))
        

   
