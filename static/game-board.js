import { submitGuess } from './submit-guess.js';

export function renderBoard(cards, status) {
    const board = document.getElementById("game-board");
    if (!board || !Array.isArray(cards)) return;

    board.innerHTML = "";
    cards.forEach(card => {
        const div = document.createElement("div");
        div.classList.add("p-4", "text-center", "rounded", "shadow", "cursor-pointer", "hover:scale-105", "transition-transform");

        if (card.visible_role === "hidden" && status === "Guess agent cards") {
            div.addEventListener("click", () => submitGuess(card.word));
        }

        if (card.visible_role != "hidden" && card.visible_role != "citizen_for_companion") {
            div.classList.add("border-2", "border-dashed", "border-gray-700");
        }

        const role = card.actual_role_for_player;
        const vrole = card.visible_role;

        switch (card.actual_role_for_player) {
            case "agent":
                if (card.visible_role === "assassin") {
                    div.classList.add("bg-black", "text-white");
                } else if (card.visible_role === "citizen") {
                    div.classList.add("bg-gray-200", "text-black");
                } else {
                    div.classList.add("bg-green-500", "text-black");
                }
                break;
            case "assassin":
                if (card.visible_role === "citizen") {
                    div.classList.add("bg-gray-200", "text-black");
                } else if (card.visible_role === "agent") {
                    div.classList.add("bg-green-500", "text-black");
                } else {
                    div.classList.add("bg-black", "text-white");
                }
                break;
            case "citizen":
                if (card.visible_role === "agent") {
                    div.classList.add("bg-green-500", "text-black");
                } else if (card.visible_role === "assassin") {
                    div.classList.add("bg-black", "text-white");
                } else {
                    div.classList.add("bg-gray-200", "text-black");
                }
                break;
            default:
                div.classList.add("bg-white");
        }

        const content = vrole !== "hidden" && vrole !== "citizen_for_companion" ? `<i class="fa-regular fa-circle-check text-2xl text-gray-700"></i>` : card.word.toUpperCase();
        div.innerHTML = `<p class="font-semibold">${content}</p>`;
        board.appendChild(div);
    });
}
