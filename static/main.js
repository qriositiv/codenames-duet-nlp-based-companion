import { setupWebSocket } from './websocket.js';
import { renderBoard } from './game-board.js';
import { updateClueUI } from './game-clue.js';
import { updateGameStatus } from './game-status.js';
import { updateScoreboard } from './game-scoreboard.js';
import { updateHistory } from './game-history.js';
import { submitGuess } from "./submit-guess.js";

setupWebSocket(updateGameUI);

function updateGameUI(gameState) {
    renderBoard(gameState.cards, gameState.status);
    updateGameStatus(gameState.status);
    updateClueUI(gameState);
    updateScoreboard(gameState);
    updateHistory(gameState.history);
}


