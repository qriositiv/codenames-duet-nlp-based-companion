import time
import numpy as np
from fastapi import APIRouter
from init import get_sbert_embedding, UNDERSTANDING_THRESHOLD, DEBUG
from dataclasses import dataclass

router = APIRouter()

@dataclass
class GuessRequest:
    clue_word: str
    clue_number: int
    word_list: list[str]

@dataclass
class WordSimilarity:
    word: str
    similarity: float

@dataclass
class GuessResponse:
    guesses: list[WordSimilarity]


@router.post("/guess/", response_model=GuessResponse)
async def guess_words_based_on_clue(req: GuessRequest) -> GuessResponse:
    start_time = time.perf_counter()
    if DEBUG:
        print(f"[DEBUG] Request: " + str(req))

    # Get the SBERT embedding for the clue word.
    clue_vector = get_sbert_embedding(req.clue_word)

    # Define list where for which word will be calculated cosine similarity with `clue_vector`.
    guess_candidates: list[WordSimilarity] = []

    # Step 1: Compute similarities with `clue_word` for each `word` in `word_list`.
    for word in req.word_list:
        word_vector = get_sbert_embedding(word)
        similarity = float(np.dot(clue_vector, word_vector))
        guess_candidates.append(WordSimilarity(word=word, similarity=similarity))

    # Step 2: Sort guesses by `similarity` in descending order.
    guess_candidates.sort(key=lambda g: g.similarity, reverse=True)

    # Step 3: Filter guesses by threshold.
    guess_candidates = [g for g in guess_candidates if g.similarity > UNDERSTANDING_THRESHOLD]

    if DEBUG:
        print(f"[DEBUG] Response: " + str(GuessResponse(guesses=guess_candidates[:req.clue_number])))
        print(f"[DEBUG] Number of words in request: {len(req.word_list)}")
        print(f"[DEBUG] guess generation executed in {(time.perf_counter() - start_time):.2f} s")

    # Return top `clue_number` guesses.
    return GuessResponse(guesses=guess_candidates[:req.clue_number])
