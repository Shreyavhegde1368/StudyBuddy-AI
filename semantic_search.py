
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


# --------------------------------------------------
# 1. EXTRACT PDF PAGES
# --------------------------------------------------

def extract_pdf_pages(pdf_file):

    reader = PdfReader(pdf_file)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        if text and text.strip():

            pages.append({
                "page": page_number,
                "text": text.strip()
            })

    return pages


# --------------------------------------------------
# 2. EXTRACT COMPLETE MCQ QUESTIONS
# --------------------------------------------------

def create_chunks(pages, chunk_size=500, overlap=100):

    chunks = []

    question_pattern = re.compile(
        r"(?<!\w)(\d{1,3})\.\s+"
    )

    for page in pages:

        text = page["text"]

        matches = list(question_pattern.finditer(text))

        if matches:

            for i, match in enumerate(matches):

                start = match.start()

                if i + 1 < len(matches):
                    end = matches[i + 1].start()
                else:
                    end = len(text)

                question_text = text[start:end].strip()

                if len(question_text) > 15:

                    chunks.append({
                        "page": page["page"],
                        "text": question_text
                    })

        else:

            # Fallback for pages without numbered questions

            start = 0

            while start < len(text):

                end = start + chunk_size

                chunk_text = text[start:end].strip()

                if chunk_text:

                    chunks.append({
                        "page": page["page"],
                        "text": chunk_text
                    })

                start += chunk_size - overlap

    return chunks


# --------------------------------------------------
# 3. CREATE SEARCH INDEX
# --------------------------------------------------

def create_index(chunks):

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True
    )

    document_vectors = vectorizer.fit_transform(texts)

    return vectorizer, document_vectors


# --------------------------------------------------
# 4. SEARCH QUESTIONS
# --------------------------------------------------

def search_notes(question, chunks, index, top_k=3):

    vectorizer, document_vectors = index

    question_vector = vectorizer.transform([question])

    similarities = cosine_similarity(
        question_vector,
        document_vectors
    )[0]

    best_indices = similarities.argsort()[::-1]

    results = []

    for chunk_index in best_indices:

        score = similarities[chunk_index]

        if score <= 0:
            continue

        result = chunks[chunk_index].copy()

        result["score"] = float(score)

        results.append(result)

        if len(results) >= top_k:
            break

    return results
