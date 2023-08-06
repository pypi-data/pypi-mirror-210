from langchain.embeddings import HuggingFaceEmbeddings, HuggingFaceInstructEmbeddings
from langchain.embeddings import HuggingFaceHubEmbeddings


def HF_text_embed(text, encoder):
    result_vector = encoder.embed_query(text)
    return result_vector