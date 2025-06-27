export function updateScoreboard(state) {
    const agentSpan = document.getElementById("agents-remaining");
    const tokenSpan = document.getElementById("time-tokens");

    if (agentSpan) agentSpan.textContent = state.agents_remain ?? "—";
    if (tokenSpan) tokenSpan.textContent = state.time_tokens_remain ?? "—";
}
