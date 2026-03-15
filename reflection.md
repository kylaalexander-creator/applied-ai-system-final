# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

1. The hints were not accurate, and would say the opposite of what it should
2. When trying to start another game, it does not work.
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

---
1. I used copilot for this project.
2. The suggestion for fixing the logic for the backwards was correct, and it caught both parts of the logic that would fix this. 
3. I asked the agent to fix the logic so that app.y and logic_utils.py matched, after the agent changed it, the entire game gave an error. I ran the error in the copilot, and then it was able to fix the mistake.

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---
I decided a bug was fixed by testing different test cases on my own. 

I tried different levels, different guessing, and multiple rounds to make sure the game was working. 

Ai helped me understand what to look for in the tests and what corrections to look from the bug fixes.

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---
I would describe it as updating the app if anything in the code changes. Any change to the code will result in the code rerunning from top to bottom, and all changes being shown. It also updates if the user presses a button, like if the game level was changed, it reruns all the code

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.

I want to take the habit of double checking the code that I let AI fix, or write. I also want to take the habit on inline ai chats, that way my prompts can be more specific. Next time, I would be a lot more specific when asking it to compare two different codes and make sure they match. I think copilot had an issue making sure the logic alligned across different pages. 
It changed the way I think about AI by reminding me that AI can make mistakes, and can sometimes make the error worse, like when the entire game gave an error. 