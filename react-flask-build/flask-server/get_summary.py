import openai
import time
import sys
import fitz  # PyMuPDF
import tiktoken
import os
import torch
from transformers import BertTokenizer, BertModel

def call_assistant_with_file(api_key, chunk):
    # Set the OpenAI API key
    openai.api_key = api_key
    
    try:
        # Create a new thread
        print("Attempting to create a new thread...")
        thread = openai.beta.threads.create()
        print(f"Thread created successfully. Thread ID: {thread.id}")

        # Add a message from the user
        try:
            print("Adding message to the thread...")
            message = openai.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=chunk
            )
            print("Message added successfully.")
        except Exception as e:
            print(f"Failed to add message to the thread. Error: {e}")
            raise

        # Create a run with the assistant
        try:
            print("Creating a run with the assistant...")
            run = openai.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id="asst_e4AK3QNJsqDWCU5tDjVioqsv"
            )
            print(f"Run created successfully. Run ID: {run.id}")
        except Exception as e:
            print(f"Failed to create a run with the assistant. Error: {e}")
            raise

        # Retrieve the run's current state
        try:
            print("Polling the run's status...")
            while True:
                run = openai.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                print(f"Current run status: {run.status}")
                if run.status == "completed":
                    print("Run completed successfully.")
                    break
                elif run.status == "failed":
                    raise Exception("The run failed to complete successfully.")
                # Wait for a short period before polling again
                time.sleep(2)
        except Exception as e:
            print(f"Failed while polling run status. Error: {e}")
            raise

        # Retrieve and print messages from the thread
        try:
            print("Retrieving messages from the thread...")
            messages = openai.beta.threads.messages.list(
                thread_id=thread.id
            )
            print("Messages retrieved successfully.")
        except Exception as e:
            print(f"Failed to retrieve messages from the thread. Error: {e}")
            raise

        # Extract the content from the first message
        try:
            result_content = messages.data[0].content[0].text.value
            print("Message content extracted successfully.")
            return result_content
        except Exception as e:
            print(f"Failed to extract message content. Error: {e}")
            raise

    except Exception as e:
        print(f"An error occurred in `call_assistant_with_file`: {e}")
        raise Exception("The run failed to complete successfully.")

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def get_text_embedding(text, max_length=1500, overlap=50):
    # Function to chunk text
    def chunk_text(text, max_length=1500, overlap=50):
        tokens = tokenizer.encode(text, add_special_tokens=True)
        chunks = []
        for i in range(0, len(tokens), max_length - overlap):
            chunk = tokens[i:i + max_length]
            chunks.append(chunk)
        return chunks

    # Chunk the text
    chunks = chunk_text(text, max_length, overlap)

    # Get embeddings for each chunk
    embeddings = []
    for chunk in chunks:
        inputs = tokenizer.decode(chunk)
        input_tensor = tokenizer(inputs, return_tensors='pt', padding=True, truncation=True)
        
        with torch.no_grad():
            outputs = model(**input_tensor)
        
        # Use the [CLS] token's embedding for each chunk
        chunk_embedding = outputs.last_hidden_state[:, 0, :]
        embeddings.append(chunk_embedding)

    # Average the chunk embeddings
    final_embedding = torch.mean(torch.stack(embeddings), dim=0)

    return final_embedding
def cosine_similarity(profile_embedding, grant_embedding):
    profile_embedding = profile_embedding.view(-1)
    grant_embedding = grant_embedding.view(-1)
    dot_product = torch.dot(profile_embedding, grant_embedding)
    norm1 = torch.norm(profile_embedding, p=2)
    norm2 = torch.norm(grant_embedding, p=2)
    cosine_sim = dot_product / (norm1 * norm2)
    return cosine_sim.item()