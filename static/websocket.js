export function setupWebSocket(updateGameUI) {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws");

    socket.onopen = () => console.log("[WebSocket] Connected");

    socket.onmessage = (event) => {
        const gameState = JSON.parse(event.data);
        //console.log("[WebSocket] Game state update:", gameState);
        updateGameUI(gameState);
    };

    socket.onerror = (err) => console.error("[WebSocket] Error:", err);
    socket.onclose = () => console.log("[WebSocket] Disconnected");
}
