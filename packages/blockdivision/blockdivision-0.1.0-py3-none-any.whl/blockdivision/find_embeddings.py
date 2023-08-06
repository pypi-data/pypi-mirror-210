import torch


# finding of embeddings
def embed(text, model, tokenizer):
    tokens = tokenizer.tokenize(text)
    # Convert tokens to IDs
    input_ids = tokenizer.convert_tokens_to_ids(tokens)
    # Convert input IDs to tensor
    input_ids_tensor = torch.tensor([input_ids])
    # Get word embeddings
    with torch.no_grad():
        outputs = model(input_ids_tensor)
        word_embeddings = outputs.last_hidden_state

    return word_embeddings