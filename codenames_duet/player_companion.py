from clue import generate_clue_based_on_word_list, WordRole
from guess import guess_words_based_on_clue, GuessRequest
from codenames_duet.enums import GameStatus
from codenames_duet.websocket_manager import manager
import random
import asyncio


game_status = ''
agents_remain = 15
time_tokens_remain = 9
cards = []
game_history = []
companion_logs = []


# Pass data for ws broadcast.
async def render_game():
    state = {
        "status": game_status,
        "agents_remain": agents_remain,
        "time_tokens_remain": time_tokens_remain,
        "cards": [{
            "word": card["word"],
            "visible_role": card["visible_role"],
            "actual_role_for_player": card["actual_role_for_player"],
            "actual_role_for_companion": card["actual_role_for_companion"]
        } for card in cards],
        "history": game_history,
    }
    await manager.broadcast(state)


# Initialisation.
async def initialize_game():
    global game_status, agents_remain, time_tokens_remain, cards, game_history, companion_logs

    game_status = ''
    agents_remain = 15
    time_tokens_remain = 9
    cards = []
    game_history = []
    companion_logs = []

    change_game_status(GameStatus.PLAYER_GENERATES_CLUE)

    with open("codenames_duet/codenames_words.txt", "r", encoding="utf-8") as f:
        word_pool = [line.strip().lower() for line in f if line.strip()]

    random.shuffle(word_pool)   
    selected_words = word_pool[:25]

    for i in range(25):
        cards.append({
            'word': selected_words[i],
            'actual_role_for_player': None,
            'actual_role_for_companion': None,
            'visible_role': 'hidden'
        })

    cards[0]['actual_role_for_player'] = 'assassin'
    cards[0]['actual_role_for_companion'] = 'assassin'

    cards[1]['actual_role_for_player'] = 'assassin'
    cards[1]['actual_role_for_companion'] = 'agent'

    cards[2]['actual_role_for_player'] = 'agent'
    cards[2]['actual_role_for_companion'] = 'assassin'

    cards[3]['actual_role_for_player'] = 'assassin'
    cards[3]['actual_role_for_companion'] = 'citizen'

    cards[4]['actual_role_for_player'] = 'citizen'
    cards[4]['actual_role_for_companion'] = 'assassin'

    for i in range(3):
        cards[i + 5]['actual_role_for_player'] = 'agent'
        cards[i + 5]['actual_role_for_companion'] = 'agent'

    for i in range(8, 18):
        if i % 2 == 0:
            cards[i]['actual_role_for_player'] = 'agent'
            cards[i]['actual_role_for_companion'] = 'citizen'
        else:
            cards[i]['actual_role_for_player'] = 'citizen'
            cards[i]['actual_role_for_companion'] = 'agent'

    for i in range(18, 25):
        cards[i]['actual_role_for_player'] = 'citizen'
        cards[i]['actual_role_for_companion'] = 'citizen'

    random.shuffle(cards)

    await render_game()


# Player give a clue (then AI guesses and gives clue back).
async def give_clue(clue_word, clue_number):
    global time_tokens_remain

    game_history.append({
        'type': 'clue',
        'word': clue_word,
        'number': clue_number,
        'log': "Your own written clue"
    })
    change_game_status(GameStatus.AI_GUESSING)
    await render_game()
    await asyncio.sleep(3)

    word_list = [card['word'] for card in cards if card['visible_role'] == 'hidden']

    guess_request = GuessRequest(clue_word, clue_number, word_list)
    guess_response = await guess_words_based_on_clue(guess_request)

    should_stop = False
    for guess in guess_response.guesses:
        for card in cards:
            if card['word'] == guess.word:
                card['visible_role'] = card['actual_role_for_player']
                game_history.append({
                    'type': 'guess',
                    'word': guess.word,
                    'role': card['actual_role_for_player'],
                    'log': str(guess.similarity)
                })
                if card['visible_role'] == 'citizen':
                    card['visible_role'] = 'citizen_for_companion'
                    change_game_status(GameStatus.AI_GENERATES_CLUE)
                    should_stop = True
                    break
        if should_stop:
            break

    await render_game()
    await asyncio.sleep(3)

    if not await is_game_over():
        time_tokens_remain -= 1
        change_game_status(GameStatus.AI_GENERATES_CLUE)
        await render_game()

        word_roles: list[WordRole] = []
        for card in cards:
            if card['visible_role'] == 'hidden' or card['visible_role'] == 'citizen_for_player':
                word_roles.append(WordRole(word=card['word'].lower(), role=card['actual_role_for_companion']))

        clue_response = await generate_clue_based_on_word_list(word_roles)
        print(clue_response)

        ai_clue = {'word': clue_response.clue_word, 'number': len(clue_response.group)}
        print (ai_clue)
        game_history.append({
            'type': 'ai_clue',
            'word': ai_clue['word'],
            'number': ai_clue['number'],
            'log': str(clue_response)
        })
        change_game_status(GameStatus.PLAYER_GUESSING)
        await render_game()


# Player guesses.
async def make_guess(guess_card):
    global time_tokens_remain
    print("guessing process")
    if guess_card == 'EndOfGuessing':
        change_game_status(GameStatus.PLAYER_GENERATES_CLUE)
        time_tokens_remain -= 1
    else:
        for card in cards:
            if card['word'] == guess_card:
                card['visible_role'] = card['actual_role_for_companion']
                game_history.append({
                    'type': 'guess',
                    'word': guess_card,
                    'role': card['visible_role'],
                    'log': "Your guess"
                })
                if card['visible_role'] == 'citizen':
                    card['visible_role'] = 'citizen_for_player'
                    change_game_status(GameStatus.PLAYER_GENERATES_CLUE)
                    break
                break

    await is_game_over()
    await render_game()


# Change game status.
def change_game_status(status: GameStatus):
    global game_status
    game_status = status


# Checks if game over.
async def is_game_over():
    global agents_remain

    agents_found = sum(1 for card in cards if card['visible_role'] == 'agent')
    agents_remain = 15 - agents_found

    if time_tokens_remain == 0:
        change_game_status(GameStatus.LAST_CHANCE)
        await render_game()
        return False

    if agents_remain == 0:
        change_game_status(GameStatus.AGENTS_FOUND)
        return True

    if time_tokens_remain < 0:
        change_game_status(GameStatus.OUT_OF_MOVES)
        return True

    for card in cards:
        if card['visible_role'] == 'assassin':
            change_game_status(GameStatus.ASSASSIN_TOUCHED)
            return True

    return False
