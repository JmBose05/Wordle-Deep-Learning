Wordle.py is a recreation of the game Wordle, with the exact same logic.

Under the run_game(self) method, a call is made to pick_answer_key(valid_wordle_answer_list, valid_wordle_answer, random_mode=True),
user can togle random_mode on or off depending on if they want to pick the answer key or not.
If random_mode = False, then the user will enter the answer key in the terminal,
otherwise the game will select a random answer key and the game will start.
