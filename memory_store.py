import os
from datetime import datetime

MEMORY_FILE = "game_memory.txt"


def save_game(record: dict) -> None:
    """Append a completed game to the plain-text memory file."""
    guesses = record.get("guesses", [])
    result = record.get("result", "unknown")
    difficulty = record.get("difficulty", "Normal")
    game_range = record.get("range", "?-?")
    attempts = record.get("attempts", 0)
    score = record.get("score", 0)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    entry = (
        f"[{timestamp}] {difficulty} ({game_range}) | "
        f"Result: {result} | Attempts: {attempts} | Score: {score} | "
        f"Guesses: {', '.join(str(g) for g in guesses)}\n"
    )

    with open(MEMORY_FILE, "a") as f:
        f.write(entry)


def load_memory_text() -> str:
    """Return the full memory file as a string, or empty string if none exists."""
    if not os.path.exists(MEMORY_FILE):
        return ""
    with open(MEMORY_FILE, "r") as f:
        return f.read().strip()


def load_total_score() -> int:
    """Sum all saved game scores from the memory file."""
    text = load_memory_text()
    if not text:
        return 0
    total = 0
    for line in text.splitlines():
        if "Score:" in line:
            try:
                total += int(line.split("Score:")[1].split("|")[0].strip())
            except (ValueError, IndexError):
                pass
    return total


def clear_memory() -> None:
    """Delete the game memory file, effectively resetting all history and score."""
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
