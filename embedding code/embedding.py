import torch
from transformers import BertTokenizer, BertModel

# Load the tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Function to chunk text
def chunk_text(text, max_length=512, overlap=50):
    tokens = tokenizer.encode(text, add_special_tokens=True)
    chunks = []
    for i in range(0, len(tokens), max_length - overlap):
        chunk = tokens[i:i + max_length]
        chunks.append(chunk)
    return chunks

# Input text (larger body of text)
long_text = "Your long input text here..."

# Chunk the text
chunks = chunk_text(long_text)

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

print(final_embedding)
