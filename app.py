import time

from codenames_duet.enums import GameStatus

start_time = time.perf_counter()

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from codenames_duet.player_companion import initialize_game, render_game, give_clue, make_guess
from codenames_duet.companion_companion import companion_companion
from codenames_duet.websocket_manager import manager
from pydantic import BaseModel
from statistics import mean
from init import DEBUG

# Start FastAPI application.
app = FastAPI()

if DEBUG:
    print(f"[DEBUG] Application fully started in {(time.perf_counter() - start_time):.2f} s")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Initialize game when app started.
@app.on_event("startup")
async def startup_event():
    await initialize_game()


# For root route display HTML file.
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Use WebSocket communication.
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await render_game()
    try:
        while True:
            await websocket.receive_text()  # keep-alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# - # Player-Companion mode.
class ClueData(BaseModel):
    clue_word: str
    clue_number: int

@app.post("/game/clue")
async def clue_endpoint(data: ClueData):
    await give_clue(data.clue_word, data.clue_number)
    return {"message": "Clue submitted successfully"}

@app.post("/game/guess")
async def guess_endpoint(word: str = Form(...)):
    await make_guess(word)
    return {"message": f"Guess '{word}' processed"}

@app.post("/game/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_game():
    await initialize_game()
    await render_game()
    return


# - # Companion-Companion mode.
@app.get("/self")
async def self_play_mode():
    runs = 5
    results = []

    for _ in range(runs):
        result = await companion_companion()
        results.append(result)

    success_count = sum(1 for r in results if r["status"] == GameStatus.AGENTS_FOUND)

    average_result = {
        "avg_agents_found": mean(r["agents_found"] for r in results),
        "avg_time_tokens_remaining": mean(r["time_tokens_remaining"] for r in results),
        "avg_total_time": mean(r["total_time"] for r in results),
        "success": success_count
    }

    return average_result
