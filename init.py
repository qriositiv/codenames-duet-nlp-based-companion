import os
import sys
import numpy as np
from sentence_transformers import SentenceTransformer

# Debugging toggle.
DEBUG = False
# Set to `True` to enable experimental rule for grouping.
EXPERIMENTAL_RULE = False

# Define where to find or save (if not exist) model.
MODEL_PATH = "sbert_model"
# Define model version.
MODEL_VERSION = "all-MiniLM-L6-v2"
# Define path to the words file, which will be synonym candidates.
WORDS_FILE = "words-1000.txt"
# Define maximum size of group which cosine similarity will be calculated.
MAX_GROUP_SIZE = 3
# Define threshold below that the similarity score is too low for synonym connections.
UNDERSTANDING_THRESHOLD = 0.35

# Synonym candidate words storage.
synonym_candidates: list[str] = []
# The same `categories` array, but storing their vectors.
synonym_candidate_vectors: np.ndarray = []

# Load Sentence-BERT (SBERT) model.
if os.path.exists(MODEL_PATH):
    # Load model from `MODEL_PATH`.
    sbert_model = SentenceTransformer(MODEL_PATH)
    print("[OK] Loading SBERT model from local storage...")
else:
    # Download model and save to `MODEL_PATH`.
    print("[Downloading] SBERT model...")
    sbert_model = SentenceTransformer(MODEL_VERSION)
    sbert_model.save(MODEL_PATH)
    print("[OK] Successfully downloaded and saved to local storage.")


# Takes a single word (string) from `category` array
# and returns the SBERT embedding as a NumPy array for `categories_vectors`.
def get_sbert_embedding(word: str):
    return sbert_model.encode(word)


# Reads words from `WORDS_FILE`, loads embeddings, and stores them in memory.
def load_categories():
    # Ensure globals are properly updated.
    global synonym_candidates, synonym_candidate_vectors

    if not os.path.exists(WORDS_FILE):
        print(f"[Error] {WORDS_FILE} not found.")
        sys.exit(1)
    else:
        # Read `WORDS_FILE` synonym candidates to `categories` array.
        with open(WORDS_FILE, "r", encoding="utf-8") as f:
            # Each line in the file corresponds to a single word.
            synonym_candidates = [line.strip() for line in f]

    print(f"[OK] Loaded {len(synonym_candidates)} categories from {WORDS_FILE}.")

    # Precompute embeddings for categories.
    synonym_candidate_vectors = np.array([get_sbert_embedding(cat) for cat in synonym_candidates])

    if len(synonym_candidate_vectors) == 0:
        raise ValueError(f"[Error] No valid categories found.")

    print(f"[OK] Precomputed {len(synonym_candidate_vectors)} category embeddings.")


# Load categories and precompute embeddings at startup.
load_categories()
