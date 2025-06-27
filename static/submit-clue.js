export async function submitClue(clueWord, clueNumber) {
    const payload = {
        clue_word: clueWord,
        clue_number: clueNumber
    };

    try {
        const response = await fetch("/game/clue", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
        } else {
            const errorText = await response.text();
            console.error("[ERROR] Clue error:", errorText);
        }
    } catch (err) {
        console.error("[ERROR] Failed to submit clue:", err);
    }
}
