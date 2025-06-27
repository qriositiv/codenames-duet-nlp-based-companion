export async function submitGuess(word) {
    try {
        const formData = new FormData();
        formData.append("word", word);
        const res = await fetch("/game/guess", { method: "POST", body: formData });
        const result = await res.json();
    } catch (err) {
        console.error("[ERROR] Guess failed:", err);
    }
}
