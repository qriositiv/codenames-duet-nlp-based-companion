from enum import Enum

class GameStatus(str, Enum):
    PLAYER_GENERATES_CLUE = "Write your clue"
    PLAYER_GUESSING = "Guess agent cards"
    AI_GUESSING = "AI is guessing"
    AI_GENERATES_CLUE = "AI generates the clue"
    LAST_CHANCE = "Time tokens run out - Guess without clues"
    AGENTS_FOUND = "All agents found"
    ASSASSIN_TOUCHED = "Assassin card touched"
    OUT_OF_MOVES = "Run out of moves"

class CardStatus(Enum):
    AGENT = "agent"
    ASSASSIN = "assassin"
    CITIZEN = "citizen"
    CITIZEN_PLAYER = "citizen_for_player"
    CITIZEN_COMPANION = "citizen_for_companion"
