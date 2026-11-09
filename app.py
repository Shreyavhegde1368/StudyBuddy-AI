
import streamlit as st
from io import BytesIO

from semantic_search import (
    extract_pdf_pages,
    create_chunks,
    create_index,
    search_notes
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="StudyVerse",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 StudyVerse")
st.subheader("Your personal AI study world")

student_name = st.text_input("What is your name?")

if student_name:
    st.success(f"Welcome to StudyVerse, {student_name}! 🎉")

st.divider()

st.header("✨ Your Study Space")

col1, col2, col3 = st.columns(3)

# --------------------------------------------------
# STUDY MATERIALS
# --------------------------------------------------

with col1:
    st.subheader("📚 Study Materials")
    st.write("Upload and explore your study notes.")

if st.button("Open Materials"):
    st.session_state.show_materials = True

# --------------------------------------------------
# PDF UPLOAD
# --------------------------------------------------

if st.session_state.get("show_materials", False):

    st.write("### Upload your study notes")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"]
    )

    if uploaded_file is not None:

        pdf_bytes = uploaded_file.getvalue()

        # Extract PDF pages
        with st.spinner("Reading your PDF..."):

            pages = extract_pdf_pages(
                BytesIO(pdf_bytes)
            )

        if not pages:

            st.warning("No readable text found in this PDF.")

        else:

            st.success("PDF uploaded successfully! 🎉")

            st.write("Number of pages:", len(pages))

            # Create chunks
            chunks = create_chunks(pages)

            if not chunks:

                st.warning("No text chunks could be created.")

            else:

                # Build semantic search index
                with st.spinner("Preparing semantic search..."):

                    index = create_index(chunks)

                st.success("StudyVerse is ready to search! 🌸")

                st.divider()

                # --------------------------------------------------
                # SEMANTIC SEARCH
                # --------------------------------------------------

                st.subheader("🧠 StudyVerse Semantic Search")

                student_question = st.text_input(
                    "Ask a question about your PDF notes"
                )

                if student_question:

                    with st.spinner("Finding relevant passages..."):

                        results = search_notes(
                            student_question,
                            chunks,
                            index,
                            top_k=3
                        )

                    st.subheader("📖 Relevant Study Material")

                    if results:

                        for number, result in enumerate(
                            results,
                            start=1
                        ):

                            st.markdown(
                                f"### Result {number}"
                            )

                            st.caption(
                                f"📄 Page {result['page']} | "
                                f"Similarity: {result['score']:.3f}"
                            )

                            st.write(result["text"])

                            st.divider()

                    else:

                        st.warning(
                            "No relevant passages were found."
                        )

                # --------------------------------------------------
                # PDF TEXT SEARCH
                # --------------------------------------------------

                st.subheader("🔎 Search Exact Words")

                search_term = st.text_input(
                    "Search a word or phrase in your PDF"
                )

                if search_term:

                    matching_pages = [
                        page
                        for page in pages
                        if search_term.lower()
                        in page["text"].lower()
                    ]

                    if matching_pages:

                        for page in matching_pages:

                            st.markdown(
                                f"**Page {page['page']}**"
                            )

                            matching_lines = [
                                line.strip()
                                for line in page["text"].splitlines()
                                if search_term.lower()
                                in line.lower()
                            ]

                            for line in matching_lines:

                                st.write(line)

                    else:

                        st.warning(
                            "No matching text found."
                        )

# --------------------------------------------------
# AI ASSISTANT CARD
# --------------------------------------------------

with col2:

    st.subheader("🧠 AI Study Assistant")
    st.write("Learn concepts and ask questions.")
    st.button("Meet Your AI")

# --------------------------------------------------
# BUNNY COMPANION CARD
# --------------------------------------------------

with col3:

    st.subheader("🐰 Bunny Companion")
    st.write("Study with your virtual friend.")
    st.button("Meet Bunny")
