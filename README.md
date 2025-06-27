# Codenames Board Game Companion Using the SBERT Language Model

Semester project done by Arsenij Nikulin, Vilnius University student. The technical documentation (pdf) located in the root directory.

## Start the Application

Install requirements
```commandline
pip install -r requirements.txt
``` 

Run FastAPI server
```commandline
uvicorn app:app --host localhost --port 8000 --reload
```

**Important!** Do not interact with system before you see in terminal:

```commandline
INFO:     Application startup complete.
```

---

## Play player-companion mode

Use interactive UI to play with companion.

Open in your browser:

```commandline
http://localhost:8000/
```

You can interact with interface in that ways:

- Write clue (*clue_word and clue_number*) and press green button "Submit".
- Guess cards by clicking them.
- Hover entities in history to get more info. 
- Start new game by clicking special button.

---

## Endpoints

### Run companion-companion mode

Special mode where AI companion plays against itself. 
You can try to change some configurations in `init.py` file to see the difference in the companion's work

GET : `http://localhost:8000/self/`

It will run 5 games in a sequence and return average results. Be prepared to wait.

### Guess processing

POST : `http://localhost:8000/guess/`

body: 
```json
{
  "clue_word": "fruit",
  "clue_number": 5,
  "word_list": ["mint", "laser", "link", "police", "fork", "africa", "night", "shot", "ghost", "dinosaur", "row", "note", "server", "green", "card", "change", "degree", "bug", "straw", "luck", "turkey", "gas", "apple", "lawyer", "moon"]
}
```

### Clue processing

POST : `http://localhost:8000/clue/`

body:
```json
[
  { "word": "mint", "role": "agent" },
  { "word": "laser", "role": "citizen" },
  { "word": "link", "role": "citizen" },
  { "word": "police", "role": "agent" },
  { "word": "fork", "role": "citizen" },
  { "word": "africa", "role": "citizen" },
  { "word": "night", "role": "citizen" },
  { "word": "shot", "role": "agent" },
  { "word": "ghost", "role": "agent" },
  { "word": "dinosaur", "role": "citizen" },
  { "word": "row", "role": "citizen" },
  { "word": "note", "role": "assassin" },
  { "word": "server", "role": "citizen" },
  { "word": "green", "role": "citizen" },
  { "word": "card", "role": "citizen" },
  { "word": "change", "role": "citizen" },
  { "word": "degree", "role": "assassin" },
  { "word": "bug", "role": "agent" },
  { "word": "straw", "role": "agent" },
  { "word": "luck", "role": "citizen" },
  { "word": "turkey", "role": "citizen" },
  { "word": "gas", "role": "agent" },
  { "word": "fan", "role": "assassin" },
  { "word": "lawyer", "role": "agent" },
  { "word": "moon", "role": "agent" }
]
```

---

## Project Structure

- `app.py` - main application file.
- `init.py` - companion's configuration, model and words loading.
- `clue.py` - companion logic to generate a clue.
- `guess.py` - companion logic to guess based on given clue.
- `requirements.txt` - libraries and packages list necessary to run application.
- `words-n.txt` - two files with synonym (clue) candidates.
- `templates/index.html` - UI to play with companion.
- `static/` - JavaScript files necessary to update UI dynamically.
- `codenames_duet/` - game implementation for both modes.

## Configurations

You can try to look at the first 20 lines in `init.py` file - this is configuration which can be changed.