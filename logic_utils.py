LEVEL_CONFIG = {
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

LEVELS = list(LEVEL_CONFIG.keys())


def get_range_for_difficulty(difficulty):
    if difficulty not in LEVEL_CONFIG:
        raise ValueError(f"Unexpected difficulty: {difficulty}")
    low, high, _ = LEVEL_CONFIG[difficulty]
    return low, high


def get_attempt_limit(difficulty):
    if difficulty not in LEVEL_CONFIG:
        raise ValueError(f"Unexpected difficulty: {difficulty}")
    _, _, attempts = LEVEL_CONFIG[difficulty]
    return attempts


def parse_guess(raw_guess):
    raw_guess = str(raw_guess).strip()
    if not raw_guess:
        return False, None, "Please enter a guess."
    try:
        guess_int = int(raw_guess)
    except ValueError:
        return False, None, "Please enter a valid integer."
    if guess_int < 1:
        return False, None, "Guess must be 1 or higher."
    return True, guess_int, None


def check_guess(guess, secret):
    try:
        secret_int = int(secret)
    except (ValueError, TypeError):
        return "Error", "Secret value is invalid."
    if guess == secret_int:
        return "Win", "Correct! You found the secret number."
    if guess < secret_int:
        return "Low", "Too low."
    return "High", "Too high."


def update_score(current_score, outcome, attempt_number):
    if outcome == "Win":
        return current_score + max(0, 100 - attempt_number * 5)
    if outcome in ("Low", "High"):
        return current_score - 1
    return current_score
