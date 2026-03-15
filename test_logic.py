import pytest
from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score

def test_get_range_for_difficulty():
    assert get_range_for_difficulty("Easy") == (1, 20)
    assert get_range_for_difficulty("Normal") == (1, 50)
    assert get_range_for_difficulty("Hard") == (1, 100)
    with pytest.raises(ValueError):
        get_range_for_difficulty("Invalid")

def test_parse_guess():
    # Valid guesses
    assert parse_guess("5") == (True, 5, None)
    assert parse_guess("  10  ") == (True, 10, None)
    # Invalid: empty
    assert parse_guess("") == (False, None, "Please enter a guess.")
    # Invalid: non-integer
    assert parse_guess("abc") == (False, None, "Please enter a valid integer.")
    # Invalid: too low
    assert parse_guess("0") == (False, None, "Guess must be 1 or higher.")

def test_check_guess():
    # Correct guess
    assert check_guess(10, 10) == ("Win", "Correct! You found the secret number.")
    # Too low
    assert check_guess(5, 10) == ("Low", "Too low.")
    # Too high
    assert check_guess(15, 10) == ("High", "Too high.")
    # Invalid secret
    assert check_guess(10, "invalid") == ("Error", "Secret value is invalid.")

def test_update_score():
    # Win on first attempt (assuming 1-based, so 100 points)
    assert update_score(0, "Win", 1) == 100
    # Win on second attempt
    assert update_score(0, "Win", 2) == 95
    # Win on many attempts, clamped to 0
    assert update_score(0, "Win", 25) == 0
    # Low/High subtracts 5, keeps multiple of 5
    assert update_score(100, "Low", 1) == 95
    assert update_score(5, "High", 1) == 0  # Clamped to 0
    # No change for other outcomes
    assert update_score(50, "Error", 1) == 50
    # Ensure always multiple of 5 and >=0
    assert update_score(3, "Low", 1) == 0  # 3-5=-2 -> 0
    assert update_score(7, "Win", 1) == 105  # 7+100=107 -> clamped to 105 (multiple of 5)
    # Another: 0 + 100 = 100, ok.
    # 100 -5 =95, ok.
    # 1 -5 = -4 ->0, ok.
    # 6 -5=1 ->0 (since 1//5=0), ok.
    # 10 -5=5, ok.
    # Seems correct.