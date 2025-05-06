from transformers import AutoTokenizer, AutoModel
import torch

# Load local BERT base model and tokenizer (no internet)
model_path = "/path/to/bert-base-uncased"  # directory with config.json, pytorch_model.bin, vocab.txt
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModel.from_pretrained(model_path, local_files_only=True)
model.eval()  # set model to evaluation mode (no dropout)

# Example sentences
candidate = "The cat is on the mat"
reference = "A cat is playing on the mat"

# Tokenize and get model outputs
inputs_c = tokenizer(candidate, return_tensors="pt")
inputs_r = tokenizer(reference, return_tensors="pt")
with torch.no_grad():
    outputs_c = model(**inputs_c)
    outputs_r = model(**inputs_r)

# Extract last hidden layer embeddings for each token (sequence length x hidden_size)
embeddings_c = outputs_c.last_hidden_state[0]  # tensor of shape [len_c, 768] for BERT-base
embeddings_r = outputs_r.last_hidden_state[0]  # tensor of shape [len_r, 768]

# Remove [CLS] and [SEP] token embeddings (the first and last positions)
embeddings_c = embeddings_c[1:-1]  # shape [len_c_tokens, 768]
embeddings_r = embeddings_r[1:-1]  # shape [len_r_tokens, 768]

# Normalize embeddings to unit length (for cosine similarity calculation)
embeddings_c = embeddings_c / embeddings_c.norm(dim=1, keepdim=True)
embeddings_r = embeddings_r / embeddings_r.norm(dim=1, keepdim=True)

# Compute cosine similarity matrix between each candidate token and each reference token
cos_sim_matrix = torch.mm(embeddings_c, embeddings_r.T)  # shape [len_c_tokens, len_r_tokens]

# Precision: average of max similarity for each candidate token
P_per_token = cos_sim_matrix.max(dim=1).values  # max over reference tokens for each candidate token
precision = P_per_token.mean().item()

# Recall: average of max similarity for each reference token
R_per_token = cos_sim_matrix.max(dim=0).values  # max over candidate tokens for each reference token
recall = R_per_token.mean().item()

# F1 score (harmonic mean of P and R)
f1 = 0.0
if precision + recall > 0:
    f1 = 2 * precision * recall / (precision + recall)

print(f"Precision = {precision:.4f}\nRecall    = {recall:.4f}\nF1        = {f1:.4f}")
