def get_range_for_difficulty(difficulty): #FIX: Refactored logic into logic_utils.py using Copilot Agent mode
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    raise ValueError(f"Unexpected difficulty: {difficulty}")


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
