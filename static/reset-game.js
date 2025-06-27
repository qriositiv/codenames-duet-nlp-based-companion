document.addEventListener("DOMContentLoaded", () => {
    const resetButton = document.getElementById("reset-button");

    if (resetButton) {
        resetButton.addEventListener("click", async () => {
            if (!confirm("Are you sure you want to start a new game?")) return;

            try {
                const res = await fetch("/game/reset", {
                    method: "POST"
                });

                if (res.ok) { } else {
                    console.error("[ERROR] Failed to reset game");
                }
            } catch (err) {
                console.error("[ERROR] Error resetting game:", err);
            }
        });
    }
});
