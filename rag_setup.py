#%% Import Libraries
import os
import glob
import shutil
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import pandas as pd
import time

#%% Configration

DOCS_DIR = "tcf_docs"
PERSIST_DIR = "chroma_store"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"   # MUST match the chat page

DISPLAY_NAMES = {}
UNIVERSITY_XLSX = "tcf_docs/university list.xlsx"  # adjust to your path
UNIVERSITY_SHEET = "list"

#Custom Funstions
def load_university_data(path=UNIVERSITY_XLSX, sheet=UNIVERSITY_SHEET):
    """One self-contained natural-language Document per row, so each
    university/field pairing embeds and retrieves as an atomic unit."""
    df = pd.read_excel(path, sheet_name=sheet)
    df = df.dropna(subset=["University Name for Policy", "Group"])
    docs = []
    for _, r in df.iterrows():
        uni        = str(r["University Name for Policy"]).strip()
        group      = str(r.get("Group", "")).strip()
        discipline = str(r.get("Discipline", "")).strip()
        city       = str(r.get("City", "")).strip()
        region     = str(r.get("Region", "")).strip()
        sector     = str(r.get("Sector", "")).strip()
        tier_raw   = r.get("Tier")
        tier       = str(tier_raw).strip().lstrip("Tt") if pd.notna(tier_raw) else ""

        descr = []
        if sector and sector.lower() != "nan": descr.append(f"a {sector.lower()} institution")
        if tier: descr.append(f"Tier {tier}")
        head = uni + (" is " + ", ".join(descr) if descr else "")
        loc = ", ".join([x for x in (city, region) if x and x.lower() != "nan"])
        if loc: head += f", located in {loc}"
        head = head.rstrip(".") + "."
        offer = f" It offers {group}"
        if discipline and discipline.lower() != "nan":
            offer += f", part of the {discipline} discipline"
        text = head + offer + "."

        docs.append(Document(
            page_content=text,
            metadata={
                "source": "TSP_University___Programme_List.xlsx",
                "display_name": "TCF Supported University & Programme List",
                "university": uni, "discipline": discipline, "group": group,
                "tier": tier, "city": city, "region": region, "sector": sector,
            },
        ))
    return docs

def prettify_filename(filename: str) -> str:
    """Turn a raw filename into a readable citation title.
    'tcf_career_guide_2024.pdf' -> 'Tcf Career Guide 2024'.
    Use DISPLAY_NAMES to override specific files with nicer titles."""
    name = os.path.splitext(filename)[0]
    name = name.replace("_", " ").replace("-", " ").replace(".", " ")
    parts = []
    for token in name.split():
        if token.isupper() and len(token) <= 4:      # keep acronyms (TCF, FBISE)
            parts.append(token)
        else:
            parts.append(token.capitalize())
    return " ".join(parts).strip() or filename

def load_text_file(path):
    """Read a .txt/.md file robustly, trying common encodings.
    Avoids LangChain's autodetect_encoding path (which has a version bug)."""
    for enc in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            with open(path, encoding=enc) as f:
                return [Document(page_content=f.read())]
        except UnicodeDecodeError:
            continue
    # latin-1 decodes any byte sequence, so it never raises — last resort.
    with open(path, encoding="latin-1") as f:
        return [Document(page_content=f.read())]

def load_documents(docs_dir: str):
    docs = []
    loaders = {
        "*.pdf":  lambda p: PyPDFLoader(p).load(),
        "*.docx": lambda p: Docx2txtLoader(p).load(),
        "*.txt":  load_text_file,
        "*.md":   load_text_file,
    }
    for pattern, load_fn in loaders.items():
        for path in glob.glob(os.path.join(docs_dir, "**", pattern), recursive=True):
            filename = os.path.basename(path)
            display = DISPLAY_NAMES.get(filename, prettify_filename(filename))
            try:
                loaded = load_fn(path)          # returns a list of Documents
                for d in loaded:
                    d.metadata["source"] = filename
                    d.metadata["display_name"] = display
                docs.extend(loaded)
                print(f'  Loaded {len(loaded):3d} section(s) from {filename}  ->  "{display}"')
            except Exception as e:
                print(f"  ! Failed to load {filename}: {e}")
    # ADD HERE
    university_docs = load_university_data()
    docs.extend(university_docs)

    print(f"  Loaded {len(university_docs):3d} university records")
    return docs

def main():
    # Ensure the docs directory exists
    if not os.path.isdir(DOCS_DIR):
        os.makedirs(DOCS_DIR, exist_ok=True)
        print(f"Created empty {DOCS_DIR}/ — add TCF documents and re-run.")
        return

    print(f"Loading documents from ./{DOCS_DIR}/ ...")
    docs = load_documents(DOCS_DIR)
    if not docs:
        print("No documents found. Add .pdf/.docx/.txt/.md files and re-run.")
        return

    print(f"\nSplitting {len(docs)} section(s) into chunks "
          f"(size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}) ...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    if not chunks:
        print("Documents loaded but produced no text chunks. Are they scanned/"
              "image-only PDFs? Those need OCR before they can be embedded.")
        return
    print(f"  -> {len(chunks)} chunks")

    # Rebuild cleanly: remove any existing store so we don't append duplicates.
    if os.path.isdir(PERSIST_DIR):
        print(f"\nRemoving existing {PERSIST_DIR}/ to rebuild from scratch ...")
        shutil.rmtree(PERSIST_DIR)

    print(f"Embedding with {EMBED_MODEL} (runs locally, no API key needed) ...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    print(f"Persisting vector store to ./{PERSIST_DIR}/ ...")
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
    )

    # Summary
    indexed = sorted({d.metadata.get("display_name", "?") for d in docs})
    print("\nDone. Indexed sources:")
    for name in indexed:
        print(f"  - {name}")
    print(f"\n{len(chunks)} chunks embedded into ./{PERSIST_DIR}/.")
    print("Remember to COMMIT ./chroma_store/ so it deploys to Streamlit Cloud.")


if __name__ == "__main__":
    main()
