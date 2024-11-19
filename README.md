Project: PDF Upload and Similarity Computation API

Overview

This project is a Flask API combined with a React frontend that allows users to upload PDF files to two separate folders, compute the similarity between the content, and manage the uploaded files. The backend processes the PDFs, extracts text, and computes similarity, while the frontend provides an easy-to-use interface for interacting with the API.

Dependencies

Below are the dependencies needed for both the backend (Python/Flask) and frontend (React).

Backend Dependencies (Python)

Flask: The main web framework used to create the API.

Installation: pip install Flask

Flask-CORS: Enables Cross-Origin Resource Sharing, which allows the frontend to interact with the backend.

Installation: pip install Flask-CORS

tiktoken: A tokenizer used for managing and limiting the size of input text during the summarization process.

Installation: pip install tiktoken

dotenv: Loads environment variables from a .env file.

Installation: pip install python-dotenv

PyMuPDF (fitz): Used for extracting text from PDF files.

Installation: pip install PyMuPDF

Transformers: Provides access to pre-trained language models for text embedding.

Installation: pip install transformers

Torch: A deep learning framework, used in combination with Transformers for embedding computations.

Installation: pip install torch

Other Standard Libraries:

os, logging, time, shutil: These are part of the standard Python library and are used for file operations, logging, and managing the retry mechanism.

Frontend Dependencies (React)

React: The main framework used for creating the frontend.

Installation: Typically installed with npx create-react-app.

Fetch API: Used for making requests to the Flask API. No additional installation is needed as it is part of modern JavaScript.

Functionalities

Backend Functionalities (Flask API)

Upload PDF Files:

Endpoint: /upload/folder1 and /upload/folder2

Method: POST

Description: Allows users to upload PDF files to either uploads_folder_1 or uploads_folder_2. The files are saved in their respective folders.

Compute Similarity:

Endpoint: /compute_similarity

Method: POST

Description: Computes the similarity between the summarized content of the files in uploads_folder_1 and uploads_folder_2. This is done by extracting text, summarizing it using OpenAI's language model, and computing the similarity score.

Clear Uploads:

Endpoint: /clear_uploads

Method: POST

Description: Clears all files from both uploads_folder_1 and uploads_folder_2.

Get Members:

Endpoint: /members

Method: GET

Description: Returns a list of hardcoded members. This is a placeholder endpoint.

Frontend Functionalities (React)

Upload Files:

Buttons: "Upload to Folder 1" and "Upload to Folder 2"

Description: Users can select and upload files to either uploads_folder_1 or uploads_folder_2 using these buttons.

Compute Similarity:

Button: "Compute Similarity"

Description: Sends a request to the /compute_similarity endpoint to compute and display the similarity score between the files in the two folders.

Clear Uploads:

Button: "Clear Uploads"

Description: Clears all the files from both upload folders by calling the /clear_uploads endpoint.

Status Messages:

Upload Status: Displays whether file uploads were successful or if there were any errors.

Similarity Result: Displays the similarity score or any errors during the computation process.

How to Run the Project

Backend (Flask API)

Clone the repository.

Create a virtual environment (optional but recommended):

python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

Install dependencies:

pip install -r requirements.txt

Create a .env file and add your OpenAI API key:

API_KEY=your_openai_api_key_here

Run the server:

python server.py

The server should start on http://localhost:5000.

Frontend (React)

Navigate to the frontend directory (if it is separate).

Install dependencies:

npm install

Run the React application:

npm start

The React app should start on http://localhost:3000.

Usage

Upload Files: Use the frontend to upload PDF files to Folder 1 and Folder 2.

Compute Similarity: After uploading, click "Compute Similarity" to calculate the similarity score between the two sets of files.

Clear Uploads: To remove all uploaded files, click "Clear Uploads".



