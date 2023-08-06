import openai
import tiktoken


def token_length(text: str) -> int:
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)


def split_text(text, chunk_size, overlap_size):
    chunks = []
    num_chunks = len(text)//(chunk_size-overlap_size)
    for i in range(num_chunks):
        start = i * (chunk_size - overlap_size)
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

    return chunks


def chunks(context: dict, metadata: dict) -> list:
    results = []
    results.append(context['toc'])
    for page, text in enumerate(context['fulltext']):
        chunks = split_text(text, 1024, 32)
        for chunk in chunks:
            chunks_with_metadata = f"[PDF-PAGE]: {page};\t[PAPER-TITLE]: {metadata['title']};\t[PAPER-CONTENT]: {chunk};"
            results.append(chunks_with_metadata)

    return results


def encode(chunks: list) -> list:
    response = openai.Embedding.create(
        input=chunks,
        model="text-embedding-ada-002",
    )

    return response['data']

