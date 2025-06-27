export function updateGameStatus(status) {
    const container = document.getElementById("game-status");
    const icon = container?.querySelector(".fa-solid");
    const text = container?.querySelector("p");

    if (!icon || !text) return;

    icon.className = "fa-solid text-2xl";
    text.textContent = status;

    switch (status) {
        case "PLAYER_GENERATES_CLUE":
        case "Guess agent cards":
            icon.classList.add("fa-user");
            break;
        case "AI generates the clue":
        case "AI is guessing":
            icon.classList.add("fa-robot");
            break;
        case "Time tokens run out - Guess without clues":
            icon.classList.add("fa-hourglass-end");
            break;
        default:
            icon.classList.add("fa-flag-checkered");
    }
}
