# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [ ] Describe the game's purpose.
- The purpose of the game is to guess a number, based on hints of higher or lower, or no hints at all. There are multiple difficulty levels that increase/decrease the guessing range.
- [ ] Detail which bugs you found.
- The bugs found include the hints being backwards, and directing the player incorrectly. Another bug was the inability to start a new game. 
- [ ] Explain what fixes you applied.
- The boolean to check if the guess should be higher or lower was fixed, and the method to start a new game was fixed.

## 📸 Demo

- [ ] [Insert a screenshot of your fixed, winning game here]
![alt text](image.png)


## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, insert a screenshot of your Enhanced Game UI here]
![alt text](image-2.png)
