from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tiktoken
from file_manip import is_folder_empty, extract_text_from_pdfs_in_folder, split_text_into_chunks
from get_summary import call_assistant_with_file , get_text_embedding, cosine_similarity
from dotenv import load_dotenv
import logging
import time
import shutil
from flask_socketio import SocketIO, emit
import torch

load_dotenv() 

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

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

@app.route("/clear_uploads", methods=["POST"])

def clear_uploads():
    try:
        shutil.rmtree(UPLOAD_FOLDER_1)
        os.makedirs(UPLOAD_FOLDER_1)
        shutil.rmtree(UPLOAD_FOLDER_2)
        os.makedirs(UPLOAD_FOLDER_2)
        logging.info("Upload folders cleared successfully.")
        return jsonify({"message": "Upload folders cleared successfully."}), 200
    except Exception as e:
        logging.error(f"Error occurred while clearing upload folders: {e}")
        return jsonify({"error": f"An error occurred while clearing upload folders: {e}"}), 500

def upload_files_to_folder(folder):
    try:
        if 'files' not in request.files:
            logging.error("No file part in the request.")
            return jsonify({"error": "No file part in the request"}), 400

        files = request.files.getlist('files')
        
        if len(files) == 0:
            logging.error("No files selected for upload.")
            return jsonify({"error": "No files selected"}), 400

        response_data = []
        for file in files:
            if file.filename != '':
                file_path = os.path.join(folder, file.filename)
                try:
                    file.save(file_path)
                    response_data.append({'filename': file.filename, 'status': 'Uploaded successfully'})
                except Exception as e:
                    logging.error(f"Error saving file {file.filename}: {e}")
                    response_data.append({'filename': file.filename, 'status': f'Failed to upload: {e}'})

        logging.info(f"Files uploaded with statuses: {response_data}")
        return jsonify({"message": "Files processed", "files": response_data}), 200

    except Exception as e:
        logging.error(f"Error occurred during file upload: {e}")
        return jsonify({"error": f"An error occurred during file upload: {e}"}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@app.route("/compute_similarity", methods=["POST"])
def compute_similarity():
    try:
        # Check if folders are empty
        if is_folder_empty(UPLOAD_FOLDER_1) or is_folder_empty(UPLOAD_FOLDER_2):
            logging.warning("One or both folders are empty.")
            return jsonify({"error": "One or both folders are empty. Please upload files to both folders before computing similarity."}), 400

        api_key = os.getenv("API_KEY")
        if not api_key:
            logging.error("API_KEY is not set. Please check your .env file.")
            return jsonify({"error": "API_KEY is not set. Please check your .env file."}), 500

        # Process research paper
        logging.info("Processing PDFs in folder 1...")
        final_rsrch_sum = process_pdfs_in_folder(UPLOAD_FOLDER_1, api_key)

        # Process each grant file individually
        logging.info("Processing PDFs in folder 2...")
        grant_summaries = process_each_pdf_in_folder(UPLOAD_FOLDER_2, api_key)

        # Get embedding for research paper
        rsrch_embedding = get_text_embedding(final_rsrch_sum)

        matched_grants = []
        for grant_summary in grant_summaries:
            grant_embedding = get_text_embedding(grant_summary['summary'])
            similarity_score = cosine_similarity(rsrch_embedding, grant_embedding)

            matched_grants.append({
                'id': grant_summary['id'],
                'title': grant_summary['title'],
                'abstract': grant_summary['abstract'],
                'fundingAmount': grant_summary['fundingAmount'],
                'deadline': grant_summary['deadline'],
                'score': similarity_score,
            })

        # Sort grants by similarity score
        matched_grants.sort(key=lambda x: x['score'], reverse=True)

        # Return top 3 matches
        top_matches = matched_grants[:3]

        logging.info("Similarity computed successfully.")
        return jsonify({"message": "Similarity computed successfully", "results": top_matches}), 200

    except Exception as e:
        logging.error(f"Error occurred during similarity computation: {e}")
        return jsonify({"error": f"An error occurred during similarity computation: {e}"}), 500

def process_pdfs_in_folder(folder_path, api_key):
    try:
        # Step 1: Extracting text
        socketio.emit('progress', {'message': 'Extracting text from your file...'})
        extracted_texts = extract_text_from_pdfs_in_folder(folder_path)
        socketio.emit('progress', {'message': 'Text extraction completed.'})

        # Step 2: Summarize each chunk
        socketio.emit('progress', {'message': 'Summarizing text...'})
        individual_summaries = []
        for pdf_text in extracted_texts:
            chunks = split_text_into_chunks(pdf_text['content'])
            for chunk in chunks:
                summary = call_assistant_with_file(api_key, chunk)
                individual_summaries.append(summary)
        combined_summary = " ".join(individual_summaries)
        socketio.emit('progress', {'message': 'Summarization completed.'})

        # Step 3: Generate embeddings
        socketio.emit('progress', {'message': 'Generating embeddings...'})
        embeddings = get_text_embedding(combined_summary)
        socketio.emit('progress', {'message': 'Embeddings generated.'})

        # Step 4: Calculating similarity scores
        socketio.emit('progress', {'message': 'Calculating similarity scores...'})
        # Assuming similarity calculation logic is defined elsewhere
        # similarity_scores = calculate_similarity(embeddings)
        socketio.emit('progress', {'message': 'Similarity scores calculated.'})

        # Step 5: Identifying top matches
        socketio.emit('progress', {'message': 'Identifying top matches...'})
        # Assuming top match identification logic is defined elsewhere
        # top_matches = identify_top_matches(similarity_scores)
        socketio.emit('progress', {'message': 'Top matches identified.'})

        # Indicate completion
        socketio.emit('progress', {'message': 'Processing complete.'})

        return combined_summary

    except Exception as e:
        logging.error(f"Error occurred during PDF processing: {e}")
        socketio.emit('progress', {'message': f'Error: {str(e)}'})
        raise

def process_each_pdf_in_folder(folder_path, api_key):
    summaries = []
    extracted_texts = extract_text_from_pdfs_in_folder(folder_path)
    
    for idx, pdf_text in enumerate(extracted_texts):
        # Process text summarization for each PDF content
        combined_summary = process_text_summarization(pdf_text['content'], api_key)
        
        # Append the summary and metadata to the summaries list
        summaries.append({
            'id': idx + 1,  # Assign a unique ID for each grant
            'title': os.path.basename(pdf_text['file']),  # Use the file name as the title
            'abstract': combined_summary,  # Use the summary as the abstract
            'fundingAmount': 'N/A',  # Replace with actual data if available
            'deadline': 'N/A',       # Replace with actual data if available
            'summary': combined_summary,
        })
    
    return summaries

def check_gpu_configuration():
    # Check if CUDA is available
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")

    if cuda_available:
        # Get the number of GPUs
        device_count = torch.cuda.device_count()
        print(f"Number of GPUs: {device_count}")

        # Get the current device index
        current_device = torch.cuda.current_device()
        print(f"Current Device Index: {current_device}")

        # Get the name of the current device
        device_name = torch.cuda.get_device_name(current_device)
        print(f"Current Device Name: {device_name}")
    else:
        print("No GPU detected. Please ensure that CUDA and cuDNN are installed correctly.")

if __name__ == "__main__":
    try:
        if not os.path.exists(UPLOAD_FOLDER_1):
            os.makedirs(UPLOAD_FOLDER_1)
        if not os.path.exists(UPLOAD_FOLDER_2):
            os.makedirs(UPLOAD_FOLDER_2)

        logging.info("Starting Flask server...")
        socketio.run(app, debug=True)
    except Exception as e:
        logging.error(f"An error occurred while starting the server: {e}")
