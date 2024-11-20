# get_summary.py

import time
import sys
import tiktoken
import os
import torch
from transformers import BertTokenizer, BertModel, BartTokenizer, BartForConditionalGeneration
import numpy as np

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Initialize BERT tokenizer and model
bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')
bert_model.eval()  # Set the model to evaluation mode
bert_model.to(device)

# Initialize summarization tokenizer and model
summarizer_tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
summarizer_model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
summarizer_model.to(device)
summarizer_model.eval()

def summarize_text_locally(text):
    inputs = summarizer_tokenizer([text], max_length=1024, truncation=True, return_tensors='pt')
    inputs = {key: value.to(device) for key, value in inputs.items()}

    summary_ids = summarizer_model.generate(
        inputs['input_ids'],
        num_beams=4,
        max_length=200,
        early_stopping=True
    )
    summary = summarizer_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def get_text_embedding(text, max_length=512, overlap=50):
    # Function to chunk text
    def chunk_text(text, max_length=512, overlap=50):
        tokens = bert_tokenizer.encode(text, add_special_tokens=True)
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
        input_ids = torch.tensor([chunk]).to(device)
        with torch.no_grad():
            outputs = bert_model(input_ids)
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
