import time
import numpy as np
from itertools import combinations
from fastapi import APIRouter
from dataclasses import dataclass
from init import get_sbert_embedding, UNDERSTANDING_THRESHOLD, DEBUG, synonym_candidates, synonym_candidate_vectors, \
    MAX_GROUP_SIZE, EXPERIMENTAL_RULE

router = APIRouter()

@dataclass(frozen=True)
class WordRole:
    word: str
    role: str

@dataclass
class WordSynonym:
    word_role: WordRole
    synonym: str
    similarity: float

@dataclass
class WordRoleSimilarity:
    word_role: WordRole
    similarity: float

@dataclass
class ClueResponse:
    clue_word: str
    group: list[WordRoleSimilarity]
    group_similarity: float


@router.post("/clue/", response_model=ClueResponse)
async def generate_clue_based_on_word_list(req: list[WordRole]) -> ClueResponse:
    start_time = time.perf_counter()
    if DEBUG:
        print(f"[DEBUG] Request: " + str(req))

    # Define list of synonym vectors which in the future will be filtered.
    filtered_synonym_vectors: list[tuple[str, np.ndarray]] = list(zip(synonym_candidates, synonym_candidate_vectors))

    # Calculate vectors for words in `req`.
    word_vectors: dict[WordRole, np.ndarray] = {wr: get_sbert_embedding(wr.word) for wr in req}

    # Step 1: Remove exact matches with words in `req`.
    excluded_words = {wr.word.lower() for wr in req}
    filtered_synonym_vectors = [
        (synonym, vec)
        for (synonym, vec) in filtered_synonym_vectors
        if synonym.lower() not in excluded_words
    ]

    # Step 2: Remove synonyms too similar to any 'assassin' word.
    for word_role in req:
        if word_role.role == 'assassin':
            assassin_vector = word_vectors[word_role]
            filtered_synonym_vectors = [
                (synonym, vec)
                for (synonym, vec) in filtered_synonym_vectors
                if float(np.dot(assassin_vector, vec)) <= UNDERSTANDING_THRESHOLD
            ]

    # Step 3: Store synonyms for non-assassin words.
    word_synonyms: list[WordSynonym] = []
    for word_role, word_vector in word_vectors.items():
        if word_role.role != 'assassin':
            for synonym, synonym_vector in filtered_synonym_vectors:
                similarity = float(np.dot(word_vector, synonym_vector))
                word_synonyms.append(
                    WordSynonym(word_role=word_role, synonym=synonym, similarity=similarity)
                )

    # Step 4: Based on rules A and B build valid word groups.
    agents = [wr for wr in req if wr.role == 'agent']
    citizens = [wr for wr in req if wr.role == 'citizen']

    groups: list[list[WordRole]] = []

    # From 1 to 5 agents.
    for k in range(1, MAX_GROUP_SIZE + 1):
        for combo in combinations(agents, k):
            groups.append(list(combo))

    # EXPERIMENTAL RULE: from 2 to 4 agents and 1 civilian.
    if EXPERIMENTAL_RULE:
        for k in range(2, MAX_GROUP_SIZE):
            for agent_combo in combinations(agents, k):
                for citizen in citizens:
                    groups.append(list(agent_combo) + [citizen])

    # Step 5: Build similarity lookup.
    similarity_lookup: dict[tuple[str, str], float] = {
        (ws.word_role.word, ws.synonym): ws.similarity
        for ws in word_synonyms
    }

    # Step 6: Score each group + synonym
    best_clue: str = ""
    best_group: list[WordRoleSimilarity] = []
    best_score: float = 0.0
    iteration_count = 0

    for group in groups:
        for synonym, _ in filtered_synonym_vectors:
            group_similarities: list[WordRoleSimilarity] = []
            similarity_sum = 0.0
            words_below_threshold = 0
            iteration_count += 1

            for wr in group:
                # Sum similarity scores for each word in group to get total similarity.
                sim = similarity_lookup.get((wr.word, synonym), 0.0)
                group_similarities.append(WordRoleSimilarity(word_role=wr, similarity=sim))
                similarity_sum += sim
                if sim < UNDERSTANDING_THRESHOLD:
                    words_below_threshold += 1

            # Total similarity adjustment.
            if words_below_threshold > 1:
                similarity_sum = 0
            else:
                similarity_sum += len(group) * len(group) * 0.01

            # Compare scores to keep the best.
            if similarity_sum > best_score:
                best_score = similarity_sum
                best_group = group_similarities
                best_clue = synonym

    if DEBUG:
        print(f"[DEBUG] Response: " + str(ClueResponse(clue_word=best_clue, group=best_group, group_similarity=best_score)))
        print(f"[DEBUG] Number of filtered synonyms: {len(filtered_synonym_vectors)}")
        print(f"[DEBUG] Number of groups: {len(groups)}")
        print(f"[DEBUG] Total group+synonym loop iterations: {iteration_count}")
        print(f"[DEBUG] clue generation executed in {(time.perf_counter() - start_time):.2f} s")

    return ClueResponse(
        clue_word=best_clue,
        group=best_group,
        group_similarity=best_score
    )
