from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Set an upload folder (ensure this directory exists or create it)
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/members")
def members():
    return jsonify({"members": ["Member1", "Member2", "Member3"]})

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
