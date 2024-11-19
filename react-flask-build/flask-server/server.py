from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tiktoken
from file_manip import is_folder_empty, extract_text_from_pdfs_in_folder, split_text_into_chunks
from get_summary import call_assistant_with_file , get_text_embedding, cosine_similarity
from dotenv import load_dotenv
import logging
import time

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER_1 = './uploads_folder_1'
UPLOAD_FOLDER_2 = './uploads_folder_2'
app.config['UPLOAD_FOLDER_1'] = UPLOAD_FOLDER_1
app.config['UPLOAD_FOLDER_2'] = UPLOAD_FOLDER_2

@app.route("/members")
def members():
    return jsonify({"members": ["Member1", "Member2", "Member3"]})

@app.route("/upload/folder1", methods=["POST"])
def upload_file_folder1():
    return upload_files_to_folder(app.config['UPLOAD_FOLDER_1'])

@app.route("/upload/folder2", methods=["POST"])
def upload_file_folder2():
    return upload_files_to_folder(app.config['UPLOAD_FOLDER_2'])

def upload_files_to_folder(folder):
    try:
        if 'files' not in request.files:
            logging.error("No file part in the request.")
            return jsonify({"error": "No file part in the request"}), 400

        files = request.files.getlist('files')
        
        if len(files) == 0:
            logging.error("No files selected for upload.")
            return jsonify({"error": "No files selected"}), 400

        saved_files = []
        for file in files:
            if file.filename != '':
                file_path = os.path.join(folder, file.filename)
                file.save(file_path)
                saved_files.append(file_path)

        logging.info(f"Files uploaded successfully: {saved_files}")
        return jsonify({"message": "Files uploaded successfully", "file_paths": saved_files}), 200

    except Exception as e:
        logging.error(f"Error occurred during file upload: {e}")
        return jsonify({"error": f"An error occurred during file upload: {e}"}), 500

@app.route("/compute_similarity", methods=["POST"])
def compute_similarity():
    try:
        if is_folder_empty(UPLOAD_FOLDER_1) or is_folder_empty(UPLOAD_FOLDER_2):
            logging.warning("One or both folders are empty.")
            return jsonify({"error": "One or both folders are empty. Please upload files to both folders before computing similarity."}), 400

        api_key = os.getenv("API_KEY")
        if not api_key:
            logging.error("API_KEY is not set. Please check your .env file.")
            return jsonify({"error": "API_KEY is not set. Please check your .env file."}), 500

        logging.info("Processing PDFs in folder 1...")
        final_rsrch_sum = process_pdfs_in_folder(UPLOAD_FOLDER_1, api_key)
        logging.info("Processing PDFs in folder 2...")
        final_grant_sum = process_pdfs_in_folder(UPLOAD_FOLDER_2, api_key)

        grnt_embedding = get_text_embedding(final_grant_sum)
        rsrch_embedding = get_text_embedding(final_rsrch_sum)

        # Placeholder for actual similarity computation
        similarity_score = cosine_similarity(grnt_embedding,rsrch_embedding)

        logging.info("Similarity computed successfully.")
        return jsonify({"message": "Similarity computed successfully", "similarity_score": similarity_score}), 200

    except Exception as e:
        logging.error(f"Error occurred during similarity computation: {e}")
        return jsonify({"error": f"An error occurred during similarity computation: {e}"}), 500

def process_pdfs_in_folder(folder_path, api_key):
    try:
        chunks_list = []

        # Step 1: Extract and split PDFs into chunks
        logging.info(f"Extracting text from PDFs in folder: {folder_path}")
        extracted_texts = extract_text_from_pdfs_in_folder(folder_path)
        for pdf_text in extracted_texts:
            chunks = split_text_into_chunks(pdf_text['content'])
            chunks_list.extend(chunks)

        # Step 2: Summarize each chunk
        individual_summaries = []
        for chunk in chunks_list:
            logging.info("Calling assistant to summarize a chunk...")
            attempt = 0
            max_attempts = 3
            while attempt < max_attempts:
                try:
                    summary = call_assistant_with_file(api_key, chunk)
                    individual_summaries.append(summary)
                    break
                except Exception as e:
                    attempt += 1
                    logging.error(f"Error during chunk summarization (attempt {attempt}): {e}")
                    if attempt == max_attempts:
                        logging.error("Max attempts reached. Failing the summarization for this chunk.")
                        raise
                    time.sleep(2)  # Wait before retrying

        # Step 3: Combine summaries and iteratively summarize until the final summary is short enough
        combined_summary = " ".join(individual_summaries)

        MAX_TOKENS = 2000
        while len(tiktoken.get_encoding("cl100k_base").encode(combined_summary)) > MAX_TOKENS:
            logging.info("Combined summary too long, splitting and summarizing again...")
            combined_chunks = split_text_into_chunks(combined_summary, max_tokens=MAX_TOKENS)
            combined_summaries = []

            for chunk in combined_chunks:
                attempt = 0
                while attempt < max_attempts:
                    try:
                        summary = call_assistant_with_file(api_key, chunk)
                        combined_summaries.append(summary)
                        break
                    except Exception as e:
                        attempt += 1
                        logging.error(f"Error during re-summarizing combined summary (attempt {attempt}): {e}")
                        if attempt == max_attempts:
                            logging.error("Max attempts reached. Failing the re-summarization for this chunk.")
                            raise
                        time.sleep(2)  # Wait before retrying

            combined_summary = " ".join(combined_summaries)

        logging.info("Final summary generated successfully.")
        return combined_summary

    except Exception as e:
        logging.error(f"Error occurred during PDF processing: {e}")
        raise

if __name__ == "__main__":
    try:
        if not os.path.exists(UPLOAD_FOLDER_1):
            os.makedirs(UPLOAD_FOLDER_1)
        if not os.path.exists(UPLOAD_FOLDER_2):
            os.makedirs(UPLOAD_FOLDER_2)

        logging.info("Starting Flask server...")
        app.run(debug=True)
    except Exception as e:
        logging.error(f"An error occurred while starting the server: {e}")
