import time
import random

from clue import generate_clue_based_on_word_list, WordRole
from guess import guess_words_based_on_clue, GuessRequest
from codenames_duet.enums import GameStatus


game_status = ''
agents_remain = 15
time_tokens_remain = 9
cards = []
game_history = []
turn_durations = []
game_start_time = None


# Change game status (only for final result).
def change_game_status(status: GameStatus):
    global game_status
    game_status = status


# Game initialisation.
def setup_cards():
    global cards
    with open("codenames_duet/codenames_words.txt", "r", encoding="utf-8") as f:
        word_pool = [line.strip().lower() for line in f if line.strip()]

    random.shuffle(word_pool)
    selected_words = word_pool[:25]
    cards = [{'word': w, 'actual_role_for_agent_a': None, 'actual_role_for_agent_b': None, 'visible_role': 'hidden'} for w in selected_words]

    # Fixed role assignment logic for demo
    cards[0]['actual_role_for_agent_a'] = 'assassin'
    cards[0]['actual_role_for_agent_b'] = 'assassin'

    cards[1]['actual_role_for_agent_a'] = 'assassin'
    cards[1]['actual_role_for_agent_b'] = 'agent'

    cards[2]['actual_role_for_agent_a'] = 'agent'
    cards[2]['actual_role_for_agent_b'] = 'assassin'

    cards[3]['actual_role_for_agent_a'] = 'assassin'
    cards[3]['actual_role_for_agent_b'] = 'citizen'

    cards[4]['actual_role_for_agent_a'] = 'citizen'
    cards[4]['actual_role_for_agent_b'] = 'assassin'

    for i in range(3):
        cards[i + 5]['actual_role_for_agent_a'] = 'agent'
        cards[i + 5]['actual_role_for_agent_b'] = 'agent'

    for i in range(8, 18):
        if i % 2 == 0:
            cards[i]['actual_role_for_agent_a'] = 'agent'
            cards[i]['actual_role_for_agent_b'] = 'citizen'
        else:
            cards[i]['actual_role_for_agent_a'] = 'citizen'
            cards[i]['actual_role_for_agent_b'] = 'agent'

    for i in range(18, 25):
        cards[i]['actual_role_for_agent_a'] = 'citizen'
        cards[i]['actual_role_for_agent_b'] = 'citizen'

    random.shuffle(cards)


# Construct WordRole[] for agent.
def get_word_roles(agent, other_agent):
    roles = []
    key = 'actual_role_for_' + agent
    for card in cards:
        if card['visible_role'] == 'hidden' or card['visible_role'] == 'visible_for' + agent:
            roles.append(WordRole(word=card['word'], role=card[key]))
    return roles


# Apply guesses (reveal cards).
def apply_guesses(guesses, agent):
    key = 'actual_role_for_' + agent
    stop = False
    for guess in guesses:
        for card in cards:
            if card['word'] == guess.word:
                role = card[key]
                card['visible_role'] = role
                game_history.append({
                    'type': 'guess',
                    'agent': agent,
                    'word': guess.word,
                    'role': role,
                    'log': str(guess.similarity)
                })
                if role == 'citizen':
                    card['visible_role'] = 'citizen_for_' + agent
                if role == 'citizen' or role == 'assassin':
                    stop = True
                break
        if stop:
            break


# How many agents left (only for final result).
def agents_left():
    return 15 - sum(1 for c in cards if c['visible_role'] == 'agent')


# Checks if game over.
def game_over():
    if agents_left() == 0:
        return True, GameStatus.AGENTS_FOUND
    if time_tokens_remain <= 0:
        return True, GameStatus.OUT_OF_MOVES
    for c in cards:
        if c['visible_role'] == 'assassin':
            return True, GameStatus.ASSASSIN_TOUCHED
    return False, ''


# Main game runtime loop.
async def companion_companion():
    global time_tokens_remain, game_start_time, game_status
    global agents_remain, cards, game_history, turn_durations

    game_status = ''
    agents_remain = 15
    time_tokens_remain = 9
    cards = []
    game_history = []
    turn_durations = []
    game_start_time = time.time()

    setup_cards()
    current_agent = 'agent_a'
    other_agent = 'agent_b'

    while True:
        turn_start = time.time()

        word_roles = get_word_roles(current_agent, other_agent)
        clue = await generate_clue_based_on_word_list(word_roles)
        game_history.append({
            'type': 'clue',
            'agent': current_agent,
            'word': clue.clue_word,
            'number': len(clue.group),
            'log': str(clue)
        })

        guess_request = GuessRequest(clue.clue_word, len(clue.group), [c['word'] for c in cards if c['visible_role'] == 'hidden' or ['visible_role'] == 'visible_for_' + current_agent])
        guess_response = await guess_words_based_on_clue(guess_request)
        apply_guesses(guess_response.guesses, current_agent)

        turn_end = time.time()
        turn_durations.append(turn_end - turn_start)

        over, status = game_over()
        if over:
            change_game_status(status)
            break

        time_tokens_remain -= 1
        current_agent, other_agent = other_agent, current_agent

    total_time = time.time() - game_start_time
    agents_found = 15 - agents_left()

    print("Game Over:", game_status)
    print(f"Total game time: {total_time:.2f} seconds")
    print(f"Turn durations (seconds): {[round(d, 2) for d in turn_durations]}")
    print(f"Time tokens remaining: {time_tokens_remain}")
    print(f"Agents found: {agents_found}")

    return {
        "status": game_status,
        "total_time": total_time,
        "turn_durations": turn_durations,
        "time_tokens_remaining": time_tokens_remain,
        "agents_found": agents_found
    }
