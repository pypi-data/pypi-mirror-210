import os
import fitz
from google.cloud import storage


def download(arxiv_id) -> str:
    os.makedirs("dataset/tmp", exist_ok=True)
    file_name = f"dataset/tmp/{arxiv_id}.pdf"
    if not os.path.exists(file_name):
        bucket_name = "arxiv-dataset"
        blob_name = f"arxiv/arxiv/pdf/{arxiv_id.split('.')[0]}/{arxiv_id}.pdf"

        storage_client = storage.Client.create_anonymous_client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(file_name)

        print(
            f"Downloaded {arxiv_id}.pdf from gs://{bucket_name}:{blob_name} successfully.")

    return file_name


def context(file_name) -> dict:
    context = {
        'toc': '',
        'fulltext': [],
    }

    toc_list = []
    with fitz.open(file_name) as doc:
        toc = doc.get_toc(simple=False)
        if len(toc) == 0:
            toc_list.append('No provided table of contents.')
        else:
            for entry in toc:
                toc_list.append(entry[1])

        for page in doc:
            text = page.get_text().encode("utf-8")
            text = text.replace(b'\n', b' ')
            context['fulltext'].append(text.decode("utf-8"))

    context['toc'] = "[Table Of Contents]: \n" + "\n".join(toc_list) + ";"

    return context


def remove(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)

        print(f"Removed {file_name} successfully.")
