import { submitGuess } from "./submit-guess.js";
import { submitClue } from "./submit-clue.js";

export function updateClueUI(gameState) {
    const form = document.getElementById("clue-form");
    const paragraph = document.getElementById("clue-text");
    const button = document.getElementById("finish-guessing");

    form.style.display = "none";
    paragraph.style.display = "none";
    button.style.display = "none";

    if (gameState.status === "Write your clue") {
        form.style.display = "block";
    } else {
        const lastClue = [...gameState.history].reverse().find(i => i.type === "clue" || i.type === "ai_clue");
        if (lastClue) {
            paragraph.innerHTML = `<strong>Clue:</strong> ${lastClue.word} (${lastClue.number})`;
            paragraph.style.display = "block";
        }

        if (gameState.status === "Guess agent cards") {
            button.textContent = "Finish guessing";
            button.style.display = "inline-block";
            button.className = "mt-2 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600";

            if (!button.hasAttribute("data-bound")) {
                button.addEventListener("click", () => submitGuess("EndOfGuessing"));
                button.setAttribute("data-bound", "true");
            }
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("clue-form");

    if (form) {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const clueWord = form.clue_word.value.trim();
            const clueNumber = parseInt(form.clue_number.value);

            if (!clueWord || isNaN(clueNumber)) {
                console.warn("[WARNING] Invalid input");
                return;
            }

            await submitClue(clueWord, clueNumber);
            form.reset();
        });
    }
});
