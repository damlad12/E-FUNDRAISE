import fitz  # PyMuPDF
import openai
import tiktoken  # Library to count tokens in text

# Function to extract text from a PDF file using PyMuPDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

# Function to count tokens using OpenAI's tokenizer (can be replaced with tiktoken)
def count_tokens(text, model="text-davinci-003"):
    enc = tiktoken.get_encoding("cl100k_base")  # Encoding for GPT-3.5 and GPT-4
    return len(enc.encode(text))

# Function to summarize text using OpenAI API
def summarize_text(text, model="text-davinci-003", max_tokens=1500):
    openai.api_key = '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'  # Replace with your OpenAI API key
    response = openai.Completion.create(
        engine=model,
        prompt=f"Please summarize the following text:\n\n{text}",
        max_tokens=max_tokens  # Adjust this based on token limits
    )
    return response.choices[0].text.strip()

# Function to split text into chunks based on token limit
def split_text_into_chunks(text, model="text-davinci-003", max_tokens=1500):
    chunks = []
    current_chunk = ""
    tokens_in_chunk = 0

    # Split the text into chunks that are within the token limit
    for line in text.split("\n"):
        token_count = count_tokens(line, model)
        if tokens_in_chunk + token_count <= max_tokens:
            current_chunk += line + "\n"
            tokens_in_chunk += token_count
        else:
            if current_chunk:  # If there's an existing chunk, save it
                chunks.append(current_chunk)
            current_chunk = line + "\n"  # Start a new chunk with the current line
            tokens_in_chunk = token_count  # Reset the token counter

    if current_chunk:  # Add the last chunk if any
        chunks.append(current_chunk)

    return chunks

# Function to process multiple PDFs and generate a single summary
def generate_summary_from_pdfs(pdf_paths, model="text-davinci-003", max_tokens=1500):
    # Combine text from all PDFs
    combined_text = ""
    for pdf_path in pdf_paths:
        pdf_text = extract_text_from_pdf(pdf_path)
        combined_text += pdf_text + "\n\n"  # Adding space between PDFs' text
    
    # Split the combined text into chunks based on the token limit
    chunks = split_text_into_chunks(combined_text, model, max_tokens)

    # Summarize each chunk
    summaries = []
    for chunk in chunks:
        summary = summarize_text(chunk, model, max_tokens)
        summaries.append(summary)

    # Combine all summaries into one final summary
    final_summary = "\n\n".join(summaries)
    return final_summary

# Example usage:
pdf_files = ['A light-in-flight single-pixel camera for use in.pdf', 'Angular momentum driven dynamics of stimulated Brillouin scattering in multimode fibers.pdf']  # List of PDF file paths
final_summary = generate_summary_from_pdfs(pdf_files)
print(final_summary)
