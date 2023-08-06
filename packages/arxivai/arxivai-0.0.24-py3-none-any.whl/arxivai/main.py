import os

import api
import embedding
import openai
import pdf
from openai.embeddings_utils import cosine_similarity, get_embedding


if __name__ == '__main__':
    arxiv_id = '2005.14165v4'  # GPT-3
    arxiv_id = '2303.08774v3'  # GPT-4
    openai.api_key = os.environ['OPENAI_API_KEY']

    metadata = api.fetch(arxiv_id)
    file_name = pdf.download(arxiv_id)
    context = pdf.context(file_name)
    chunks = embedding.chunks(context, metadata)
    print(f'chunks = {chunks}')
    # embeddings = embedding.encode(chunks)
    # print([(x[embedding]) for x in embeddings])

    # texts = [
    #     "This is a test.",
    #     "This is another test.",
    #     "This is a third test.",
    # ]
    # print(f'token length = {embedding.token_length(texts)}')

    

    # print(f'Number of chunks: {len(chunks)}')
    # print(f'Number of embeddings: {len(embeddings)}')
    # print(chunks[:3])

    # # db = embedding.vector_database(chunks, OpenAIEmbeddings())
    # # print(db.head())

    # # chain = load_qa_chain(OpenAI(temperature=0.0), chain_type="stuff")
    # db = FAISS.from_documents(chunks, OpenAIEmbeddings())
    # qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0.0), db.as_retriever())
    # chat_history = []

    # while True:
    #     question = input("Enter a question: ")
    #     if question == "exit()":
    #         break
    #     # docs = db.similarity_search(question)
    #     # answers = chain.run(input_documents=docs, question=question)
    #     # print(answers)

    #     response = qa({"question": question, "chat_history": chat_history})
    #     chat_history.append((question, response['answer']))
    #     print(f'Q: {question}')
    #     print(f'A: {response["answer"]}')

    # question_embedding = embedding.encode_sentence(question)
    # db["similarity"] = db.embedding.apply(lambda x: cosine_similarity(x, question_embedding))
    # ranks = db.sort_values(by="similarity", ascending=False)
    # print(ranks.head(n=1))

    # question_embedding = embedding.encode_sentence(question)
    # db["similarity"] = db.embedding.apply(lambda x: cosine_similarity(x, question_embedding))
    # ranks = db.sort_values(by="similarity", ascending=False)
    # print(ranks.head(n=2))

    # data = response.json()
    # items = data.get("message", {}).get("items", [])
    # if items:
    #     first_item = items[0]
    #     doi = first_item.get("DOI")
    #     if doi:
    #         print(f'Found DOI: {doi}')
    #         doi_url = f"https://doi.org/{doi}"
    #         print(f"DOI URL: {doi_url}")

    # r = requests.get('http://api.crossref.org/works?query.bibliographic="Tyler B. Smith, Momentum-space Gravity from the Quantum Geometry and Entropy of Bloch Electrons"')
    # print(r.content)
