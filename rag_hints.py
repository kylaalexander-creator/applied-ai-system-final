import os

from openai import OpenAI

from memory_store import load_memory_text

LEVELS = [f"Level {i}" for i in range(1, 11)]


def _client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _guess_pattern(history: list) -> str:
    ints = [g for g in history if isinstance(g, int)]
    if len(ints) < 2:
        return "Not enough guesses to detect a pattern yet."
    diffs = [abs(ints[i] - ints[i - 1]) for i in range(1, len(ints))]
    avg = sum(diffs) / len(diffs)
    if diffs[-1] < avg * 0.5:
        return "Narrowing in with smaller steps — good technique."
    if diffs[-1] > avg * 1.5:
        return "Taking big jumps — bold strategy."
    return "Steady, consistent step sizes."


def get_hint(
    guess: int,
    direction: str,
    attempt: int,
    max_attempts: int,
    difficulty: str,
    history: list,
    game_range: tuple[int, int],
) -> str:
    """Return a personalized in-game hint using past game history."""
    low, high = game_range
    past_games = load_memory_text()
    pattern = _guess_pattern(history)

    direction_text = (
        "Too low! Guess higher."
        if direction == "Low"
        else "Too high! Guess lower."
    )

    system = (
        "You are a chill, witty friend watching someone play a number guessing game. "
        "You have their game history. Write ONE casual sentence: tell them higher or lower, "
        "and slip in one quick observation from their past games if relevant. "
        "Sound natural, not dramatic. Never reveal the secret number."
    )

    memory_section = (
        f"Past games:\n{past_games}\n\n"
        if past_games
        else "No past games yet.\n\n"
    )

    user = (
        f"{memory_section}"
        f"Guessed {guess} on attempt {attempt}/{max_attempts} — {direction_text} "
        f"Guesses so far: {history}. Pattern: {pattern}."
    )

    resp = _client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=60,
        temperature=0.85,
    )
    return resp.choices[0].message.content.strip()


def get_game_over_message(
    result: str,
    secret: int,
    attempts: int,
    score: int,
    difficulty: str,
    history: list,
    game_range: tuple[int, int],
) -> str:
    """Return a personalized end-of-game message using past game history."""
    low, high = game_range
    past_games = load_memory_text()

    memory_section = (
        f"Past games:\n{past_games}\n\n"
        if past_games
        else "No past games yet.\n\n"
    )

    outcome_word = "won" if result == "won" else "lost"
    prompt = (
        f"You're a chill friend reacting to someone's number guessing game. Keep it to 2 short sentences. "
        f"React to the {outcome_word}, then reference something specific from their history if you can "
        f"(a pattern, improvement, or recurring habit). Sound natural and fun, not over the top.\n\n"
        f"{memory_section}"
        f"Just {outcome_word} {difficulty} (range {low}–{high}). "
        f"Secret: {secret}. Attempts: {attempts}. Score: {score}. Guesses: {history}."
    )

    resp = _client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80,
        temperature=0.85,
    )
    return resp.choices[0].message.content.strip()


def get_level_suggestion(current_level: str) -> tuple[str, str] | tuple[None, None]:
    """
    Analyzes recent performance locally, then asks GPT to write the message.
    Returns (message, new_level_name) or (None, None) if no change is warranted.
    """
    past_games = load_memory_text()
    if not past_games:
        return None, None

    level_games = [l for l in past_games.splitlines() if current_level in l and l.strip()]
    if len(level_games) < 3:
        return None, None

    recent = level_games[-3:]
    wins = sum(1 for l in recent if "Result: won" in l)
    losses = sum(1 for l in recent if "Result: lost" in l)
    level_num = int(current_level.split()[-1])

    if wins == 3 and level_num < 10:
        direction, new_level = "up", f"Level {level_num + 1}"
    elif losses == 3 and level_num > 1:
        direction, new_level = "down", f"Level {level_num - 1}"
    else:
        return None, None

    streak = "won 3 in a row" if direction == "up" else "lost 3 in a row"
    prompt = (
        f"Someone just {streak} on {current_level} of a number guessing game "
        f"and is being moved {'up' if direction == 'up' else 'down'} to {new_level} automatically. "
        f"Write ONE short, casual sentence telling them. Reference the streak. No exclamation overload."
    )

    resp = _client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60,
        temperature=0.8,
    )
    return resp.choices[0].message.content.strip(), new_level


# ── Skill Surge ───────────────────────────────────────────────────────────────

_LEVEL_RANGES = {
    "Level 1":  (1, 10,   10),
    "Level 2":  (1, 20,    9),
    "Level 3":  (1, 35,    8),
    "Level 4":  (1, 50,    8),
    "Level 5":  (1, 75,    7),
    "Level 6":  (1, 100,   7),
    "Level 7":  (1, 200,   6),
    "Level 8":  (1, 350,   6),
    "Level 9":  (1, 500,   5),
    "Level 10": (1, 1000,  5),
}


def get_skill_surge_config() -> dict | None:
    """
    Analyze past games and design a brutal 5-game Skill Surge.
    Returns a config dict or None if there is not enough history.
    """
    past_games = load_memory_text()
    if not past_games or len(past_games.splitlines()) < 5:
        return None

    range_ref = "\n".join(
        f"  {lvl}: range 1-{h}, standard attempts: {a}"
        for lvl, (_, h, a) in _LEVEL_RANGES.items()
    )

    prompt = (
        f"You are designing a brutal 5-game 'Skill Surge' challenge for a number guessing game.\n"
        f"Analyze the player's history and build 5 games that hammer their specific weak spots.\n\n"
        f"Level reference:\n{range_ref}\n\n"
        f"Player history:\n{past_games}\n\n"
        f"Rules for designing each game:\n"
        f"- Pick levels where the player loses most or uses the most attempts\n"
        f"- Set 'attempts' to 2-3 fewer than their typical count on that level (minimum 3)\n"
        f"- Make games progressively harder across the 5 challenges\n"
        f"- 'low' is always 1, 'high' must exactly match the level's range above\n\n"
        f"Return ONLY valid JSON, no markdown, no explanation:\n"
        f'{{"intro":"1-2 sentences calling out their specific weak spots","games":['
        f'{{"level":"Level X","low":1,"high":50,"attempts":4,'
        f'"challenge_name":"Short punchy name","taunt":"1 sentence on what weakness this targets"}}]}}'
    )

    resp = _client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700,
        temperature=0.7,
    )

    raw = resp.choices[0].message.content.strip()
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw

    try:
        import json
        config = json.loads(raw)
        games = config.get("games", [])
        if len(games) == 5 and "intro" in config:
            # Clamp attempts to valid range and fix high to match level
            for g in games:
                _, correct_high, std_att = _LEVEL_RANGES.get(g["level"], (1, 100, 7))
                g["high"] = correct_high
                g["low"] = 1
                g["attempts"] = max(3, min(g["attempts"], std_att - 1))
            return config
    except Exception:
        pass
    return None


def get_pregame_prediction(difficulty: str, attempt_limit: int) -> tuple[int | None, str | None]:
    """Predict attempt count for the upcoming game.
    Uses current-level history; falls back to the closest lower level if none exists."""
    past_games = load_memory_text()
    if not past_games:
        return None, None

    all_lines = [l for l in past_games.splitlines() if l.strip()]

    def _lines_for(level: str) -> list[str]:
        # Match "] Level N (" to avoid "Level 1" hitting "Level 10" lines
        tag = f"] {level} ("
        return [l for l in all_lines if tag in l]

    level_lines = _lines_for(difficulty)
    reference_level = difficulty

    if not level_lines:
        level_num = int(difficulty.split()[-1])
        for n in range(level_num - 1, 0, -1):
            candidate = f"Level {n}"
            candidate_lines = _lines_for(candidate)
            if candidate_lines:
                level_lines = candidate_lines
                reference_level = candidate
                break

    if not level_lines:
        return None, None

    history_block = "\n".join(level_lines[-6:])
    using_fallback = reference_level != difficulty

    if using_fallback:
        context_note = (
            f"They have no history on {difficulty} yet — using their {reference_level} games "
            f"as the closest reference below it."
        )
        msg_note = (
            f" Mention naturally that this is based on their {reference_level} history "
            f"since they haven't played {difficulty} before."
        )
    else:
        context_note = ""
        msg_note = ""

    prompt = (
        f"A player is about to start a game on {difficulty} (max {attempt_limit} attempts)."
        + (f" {context_note}" if context_note else "") + "\n"
        f"Their recent history on {reference_level}:\n{history_block}\n\n"
        f"Predict how many attempts they will need on {difficulty}. Reply ONLY with valid JSON, no markdown:\n"
        f'{{\"predicted\": <integer 1-{attempt_limit}>, \"message\": \"<one casual sentence>\"}}\n'
        f"The message should reference a specific pattern you noticed — keep it natural and brief."
        + msg_note
    )

    resp = _client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.7,
    )

    raw = resp.choices[0].message.content.strip()
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw

    try:
        import json
        data = json.loads(raw)
        pred = int(data["predicted"])
        pred = max(1, min(pred, attempt_limit))
        return pred, data["message"]
    except Exception:
        return None, None


def get_pregame_reveal(predicted: int, actual: int, result: str) -> str:
    """React to how accurate the pre-game prediction was."""
    outcome = "won" if result == "won" else "lost"
    prompt = (
        f"Before the game I predicted {predicted} attempts. "
        f"The player {outcome} using {actual} attempt(s). "
        f"Write ONE short casual sentence reacting to the accuracy. "
        f"If spot-on, act smug. If they beat it, be impressed. If they did worse, tease them lightly. "
        f"If they lost, acknowledge it. Keep it under 20 words."
    )

    resp = _client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60,
        temperature=0.85,
    )
    return resp.choices[0].message.content.strip()


def get_achievements(result: str, difficulty: str, attempts: int, score: int) -> list[dict]:
    """
    Analyze full game history (after save) and return achievements just unlocked by the last game.
    Each achievement: {"title": str, "description": str}
    """
    past_games = load_memory_text()
    if not past_games:
        return []

    prompt = (
        f"A player just finished a game. Look at their COMPLETE history below and identify "
        f"which achievements were JUST unlocked by their most recent game (the last line). "
        f"Only flag achievements that are NEW — not ones already earned in earlier games.\n\n"
        f"Complete history:\n{past_games}\n\n"
        f"Most recent game — Level: {difficulty}, Result: {result}, Attempts: {attempts}, Score: {score}\n\n"
        f"Check ONLY these milestones:\n"
        f"- First win ever\n"
        f"- First win on this specific level\n"
        f"- Won in exactly 1 attempt\n"
        f"- Won in exactly 2 attempts\n"
        f"- Win streak of 3 games in a row (any level)\n"
        f"- Win streak of 5 games in a row (any level)\n"
        f"- Beat personal best attempt count on this level\n"
        f"- 10th, 25th, or 50th total game played\n"
        f"- First time completing Level 10\n"
        f"- Lost 3 in a row (consolation badge: 'Persistent')\n\n"
        f"Return ONLY a valid JSON array, no markdown, no explanation:\n"
        f'[{{"title": "Short Name", "description": "One casual sentence."}}]\n'
        f"Return [] if nothing new was unlocked."
    )

    resp = _client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=350,
        temperature=0.7,
    )

    raw = resp.choices[0].message.content.strip()
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw

    try:
        import json
        result_list = json.loads(raw)
        if isinstance(result_list, list):
            return result_list
    except Exception:
        pass
    return []


def get_surge_summary(results: list[dict], total_score: int) -> str:
    """Return a GPT-written summary of a completed Skill Surge."""
    past_games = load_memory_text()

    wins = sum(1 for r in results if r["result"] == "won")
    losses = len(results) - wins
    lines = "\n".join(
        f"Game {i+1} ({r['level']}): {r['result']} in {r['attempts']} attempts, score {r['score']}"
        for i, r in enumerate(results)
    )

    prompt = (
        f"A player just finished a 5-game Skill Surge (designed to target their weak spots).\n\n"
        f"Results:\n{lines}\n"
        f"Total surge score: {total_score}. Wins: {wins}/5.\n\n"
        f"Past history context:\n{past_games or 'N/A'}\n\n"
        f"Write 2-3 casual sentences summarizing their surge performance. "
        f"Be honest — if they did badly, say so. Reference a specific game or pattern. "
        f"End with what they should work on."
    )

    resp = _client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120,
        temperature=0.85,
    )
    return resp.choices[0].message.content.strip()
