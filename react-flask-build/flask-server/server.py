from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # This allows all domains to access the server. You can specify origins if needed.

# Set upload folders (ensure these directories exist or create them)
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
    if 'files' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    files = request.files.getlist('files')
    
    if len(files) == 0:
        return jsonify({"error": "No files selected"}), 400

    saved_files = []
    for file in files:
        if file.filename != '':
            file_path = os.path.join(folder, file.filename)
            file.save(file_path)
            saved_files.append(file_path)

    return jsonify({"message": "Files uploaded successfully", "file_paths": saved_files}), 200

@app.route("/compute_similarity", methods=["POST"])
def compute_similarity():
    # Placeholder similarity computation logic
    similarity_score = 0.85  # Replace with actual similarity computation logic
    return jsonify({"message": "Similarity computed successfully", "similarity_score": similarity_score}), 200

if __name__ == "__main__":
    # Create the upload folders if they do not exist
    if not os.path.exists(UPLOAD_FOLDER_1):
        os.makedirs(UPLOAD_FOLDER_1)
    if not os.path.exists(UPLOAD_FOLDER_2):
        os.makedirs(UPLOAD_FOLDER_2)
    app.run(debug=True)
