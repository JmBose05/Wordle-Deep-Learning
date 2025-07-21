import pygame
import random

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
WINDOW_TITLE = "AI WORDLE PROJECT"

# Grid dimensions
RECT_WIDTH = 100
RECT_HEIGHT = 100
DIST_BETWEEN_RECT = 15
GRID_ROWS = 6
GRID_COLS = 5

# Layout constants
DIST_TO_TOP_BORDER = 100
DIST_TO_SIDE_BORDER = 120
TITLE_Y_POSITION = 50

# Letter display
LETTER_SIZE = 30
LETTER_SPACING = 25
ALPHABET_X_START = 15
ALPHABET_COLUMN_WIDTH = 40
LETTERS_PER_COLUMN = 13

# Endscreen
ENDSCREEN_WIDTH = 700
ENDSCREEN_HEIGHT = 400
ENDSCREEN_X_POS = 50
ENDSCREEN_Y_POS = 200

# Font sizes
TITLE_FONT_SIZE = 100
TILE_FONT_SIZE = 48
ERROR_FONT_SIZE = 48
ENDSCREEN_FONT_SIZE = 60

# Colors
COLOR_WHITE = "white"
COLOR_BLACK = "black"
COLOR_GREY = "grey"
COLOR_YELLOW = "yellow"
COLOR_GREEN = "green"
COLOR_RED = "red"
COLOR_LIGHTGRAY = "lightgray"

# Game states
STATE_BLANK = 'Blank'
STATE_BLACK = 'Black'
STATE_YELLOW = 'Yellow'
STATE_GREEN = 'Green'

# Timing
INVALID_MESSAGE_DURATION = 2000
FPS = 60

# Error messages
MSG_NEED_FIVE_LETTERS = "Need 5 letters!"
MSG_INVALID_WORD = "Invalid word!"
MSG_WINNER = "Winner!"
MSG_YOU_LOST = "You Lost!"

class WordleGame:
    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(WINDOW_TITLE)
        
        self.rect_width = RECT_WIDTH
        self.rect_height = RECT_HEIGHT
        self.dist_between_rect = DIST_BETWEEN_RECT
        self.dist_to_top_border = DIST_TO_TOP_BORDER
        self.dist_to_side_border = DIST_TO_SIDE_BORDER
        self.size_of_letter = LETTER_SIZE
        self.dist_between_letters = LETTER_SPACING
        self.endscreen_width = ENDSCREEN_WIDTH
        self.endscreen_height = ENDSCREEN_HEIGHT
        self.endscreen_x_pos = ENDSCREEN_X_POS
        self.endscreen_y_pos = ENDSCREEN_Y_POS
        
        self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.title_surface = self.title_font.render("WORDLE", True, COLOR_BLACK)
        self.title_text = self.title_surface.get_rect()
        self.title_text.center = (screen_width // 2, TITLE_Y_POSITION)
        self.letter_font = pygame.font.Font(None, self.size_of_letter)
        self.tile_font = pygame.font.Font(None, TILE_FONT_SIZE)

    def initialize_game(self):
        with open('valid_wordle_answer.txt', 'r') as answer_key_file:
            valid_wordle_answer = set(word.strip() for word in answer_key_file)
        
        with open('valid_wordle_guess.txt', 'r') as guess_key_file:
            valid_wordle_guess = set(word.strip() for word in guess_key_file)
        
        valid_wordle_answer_list = list(valid_wordle_answer)

        return valid_wordle_answer, valid_wordle_guess, valid_wordle_answer_list

        return valid_wordle_answer, valid_wordle_guess, valid_wordle_answer_list

    def initialize_game_state(self):
        available_letters = {chr(i): COLOR_BLACK for i in range(ord('a'), ord('z') + 1)}
        
        game_grid_state = [[STATE_BLANK for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        game_grid_letters = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        return available_letters, game_grid_state, game_grid_letters
    
    def is_valid_answer(self, guess, valid_answers):
        return guess.lower() in valid_answers

    def is_valid_guess(self, guess, valid_guesses):
        return guess.lower() in valid_guesses

    def pick_answer_key(self, valid_answers_list, valid_answers, random_mode=True):
        if random_mode:
            return random.choice(valid_answers_list)
        else:
            print("Enter your answer key, or 'random' for a randomized one: ")
            while True:
                answer_key = input()
                if answer_key == 'random':
                    print("Starting game!")
                    return random.choice(valid_answers_list)
                if self.is_valid_answer(answer_key, valid_answers):
                    print("Starting game!")
                    return answer_key
                print("Invalid answer key...")
                print("Enter the key:")

    def check_guess_against_answer(self, guess, answer, state, available_letters):
        # Create a list to track which letters in answer have been matched
        answer_letters = list(answer)
        matched_positions = [False] * GRID_COLS
        
        # First pass: check for exact matches (green)
        for i in range(GRID_COLS):
            if guess[i] == answer[i]:
                state[i] = STATE_GREEN
                available_letters[guess[i]] = COLOR_GREEN
                matched_positions[i] = True
                answer_letters[i] = None  # Mark as used
        
        # Second pass: check for letters in wrong position (yellow)
        for i in range(GRID_COLS):
            if not matched_positions[i]:  # Not already green
                if guess[i] in answer_letters:
                    # Find first occurrence of this letter that hasn't been matched
                    for j in range(GRID_COLS):
                        if answer_letters[j] == guess[i]:
                            state[i] = STATE_YELLOW
                            if available_letters[guess[i]] != COLOR_GREEN:
                                available_letters[guess[i]] = COLOR_YELLOW
                            answer_letters[j] = None  # Mark as used
                            break
                else:
                    state[i] = STATE_BLACK
                    if available_letters[guess[i]] not in [COLOR_GREEN, COLOR_YELLOW]:
                        available_letters[guess[i]] = COLOR_GREY
        
        # Check if all letters match (win condition)
        return all(state[i] == STATE_GREEN for i in range(GRID_COLS))

    def draw_available_letters(self, available_letters):
        letters = list(available_letters.keys())
        for i, letter in enumerate(letters):
            col = i // LETTERS_PER_COLUMN  
            row = i % LETTERS_PER_COLUMN
            
            x_pos = ALPHABET_X_START + col * ALPHABET_COLUMN_WIDTH
            y_pos = self.dist_to_top_border + row * self.dist_between_letters
            
            color = available_letters[letter]
            letter_surface = self.letter_font.render(letter.upper(), True, color)
            letter_rect = letter_surface.get_rect()
            letter_rect.center = (x_pos, y_pos)

            self.screen.blit(letter_surface, letter_rect)

    def draw_letters(self, letters, curr_guess):
        for row in range(curr_guess + 1):
            for col in range(GRID_COLS):
                x_rect_pos = self.dist_to_side_border + col * (self.dist_between_rect + self.rect_width)
                y_rect_pos = self.dist_to_top_border + row * (self.dist_between_rect + self.rect_height)

                if letters[row][col]:
                    tile_surface = self.tile_font.render(letters[row][col].upper(), True, COLOR_BLACK)
                    tile_rect = tile_surface.get_rect()
                    tile_rect.center = (x_rect_pos + (self.rect_width // 2), y_rect_pos + (self.rect_height // 2))
                    self.screen.blit(tile_surface, tile_rect)

    def draw_grid(self, state):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x_pos = self.dist_to_side_border + col * (self.dist_between_rect + self.rect_width)
                y_pos = self.dist_to_top_border + row * (self.dist_between_rect + self.rect_height)
                rect_color = state[row][col]
                
                if rect_color == STATE_BLANK:
                    pygame.draw.rect(self.screen, COLOR_WHITE, (x_pos, y_pos, self.rect_width, self.rect_height))
                    pygame.draw.rect(self.screen, COLOR_BLACK, (x_pos, y_pos, self.rect_width, self.rect_height), width=3)
                elif rect_color == STATE_BLACK:
                    pygame.draw.rect(self.screen, COLOR_GREY, (x_pos, y_pos, self.rect_width, self.rect_height))
                elif rect_color == STATE_YELLOW:
                    pygame.draw.rect(self.screen, COLOR_YELLOW, (x_pos, y_pos, self.rect_width, self.rect_height))
                else:  # Green
                    pygame.draw.rect(self.screen, COLOR_GREEN, (x_pos, y_pos, self.rect_width, self.rect_height))

    def endscreen(self, total_guesses, answer_key, win, clock):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        return True
                    elif event.key == pygame.K_n:
                        running = False
            # Draw endscreen background
            pygame.draw.rect(self.screen, COLOR_LIGHTGRAY, (self.endscreen_x_pos, self.endscreen_y_pos, self.endscreen_width, self.endscreen_height))
            pygame.draw.rect(self.screen, COLOR_BLACK, (self.endscreen_x_pos, self.endscreen_y_pos, self.endscreen_width, self.endscreen_height), width=3)
            
            font = pygame.font.Font(None, ENDSCREEN_FONT_SIZE)
        
            if win:
                text1 = MSG_WINNER
                text2 = f"{total_guesses + 1}/{GRID_ROWS} guesses used"
            else:
                text1 = MSG_YOU_LOST
                text2 = f"{GRID_ROWS}/{GRID_ROWS} guesses used"
            
            surface1 = font.render(text1, True, COLOR_BLACK)
            rect1 = surface1.get_rect()
            rect1.center = (self.endscreen_x_pos + self.endscreen_width // 2, self.endscreen_y_pos + (self.endscreen_height // 5))
            self.screen.blit(surface1, rect1)
            
            surface2 = font.render(text2, True, COLOR_BLACK)
            rect2 = surface2.get_rect()
            rect2.center = (self.endscreen_x_pos + self.endscreen_width // 2, self.endscreen_y_pos + 2 * (self.endscreen_height // 5))
            self.screen.blit(surface2, rect2)
            
            answer_text = f"Answer: {answer_key.upper()}"
            answer_surface = font.render(answer_text, True, COLOR_BLACK)
            answer_rect = answer_surface.get_rect()
            answer_rect.center = (self.endscreen_x_pos + self.endscreen_width // 2, self.endscreen_y_pos + 3 * (self.endscreen_height // 5))
            self.screen.blit(answer_surface, answer_rect)
            
            prompt_text = "Play Again? Y/N"
            prompt_surface = font.render(prompt_text, True, COLOR_BLACK)
            prompt_rect = prompt_surface.get_rect()
            prompt_rect.center = (self.endscreen_x_pos + self.endscreen_width // 2, self.endscreen_y_pos + 4 * (self.endscreen_height // 5))
            self.screen.blit(prompt_surface, prompt_rect)
            
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def draw_invalid_message(self, need_five_letters):
        error_font = pygame.font.Font(None, ERROR_FONT_SIZE)
        if need_five_letters:
            error_text = MSG_NEED_FIVE_LETTERS
        else:
            error_text = MSG_INVALID_WORD
        error_surface = error_font.render(error_text, True, COLOR_RED)
        error_rect = error_surface.get_rect()
        error_rect.center = (self.screen.get_width() // 2, self.dist_to_top_border // 2)

        padding = 20
        bg_rect = pygame.Rect(
            error_rect.x - padding,
            error_rect.y - padding,
            error_rect.width + 2 * padding,
            error_rect.height + 2 * padding
        )
        pygame.draw.rect(self.screen, COLOR_WHITE, bg_rect)
        pygame.draw.rect(self.screen, COLOR_BLACK, bg_rect, width=2)
                
        self.screen.blit(error_surface, error_rect)

    def run_game(self):
        # Initialize game
        valid_wordle_answer, valid_wordle_guess, valid_wordle_answer_list = self.initialize_game()
        available_letters, game_grid_state, game_grid_letters = self.initialize_game_state()
        answer_key = self.pick_answer_key(valid_wordle_answer_list, valid_wordle_answer, random_mode=True)
        
        clock = pygame.time.Clock()
        game_won = False
        quit_game = False

        # Game loop
        for curr_guess in range(GRID_ROWS):
            if game_won or quit_game:
                break
                
            curr_guess_str = ''
            running = True
            show_invalid_message = False
            invalid_message_timer = 0

            while running and not quit_game:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit_game = True
                        running = False
                        break
                    elif event.type == pygame.KEYDOWN:
                        if event.unicode.isalpha() and len(event.unicode) == 1:
                            letter = event.unicode.lower()
                            if len(curr_guess_str) < GRID_COLS:
                                curr_guess_str += letter
                                game_grid_letters[curr_guess][len(curr_guess_str)-1] = letter
                        elif event.key == pygame.K_RETURN:
                            if len(curr_guess_str) == GRID_COLS and self.is_valid_guess(curr_guess_str, valid_wordle_guess):
                                running = False
                                if self.check_guess_against_answer(curr_guess_str, answer_key, game_grid_state[curr_guess], available_letters):
                                    game_won = True
                                break
                            else:
                                show_invalid_message = True
                                need_five_letters = len(curr_guess_str) < GRID_COLS
                                invalid_message_timer = pygame.time.get_ticks()
                        elif event.key == pygame.K_BACKSPACE:
                            if len(curr_guess_str) > 0:
                                curr_guess_str = curr_guess_str[:-1]
                                game_grid_letters[curr_guess][len(curr_guess_str)] = ''
                
                if show_invalid_message:
                    if pygame.time.get_ticks() - invalid_message_timer > INVALID_MESSAGE_DURATION:
                        show_invalid_message = False

                # Draw everything
                self.screen.fill(COLOR_WHITE)
                self.screen.blit(self.title_surface, self.title_text)
                self.draw_available_letters(available_letters)
                self.draw_grid(game_grid_state)
                self.draw_letters(game_grid_letters, curr_guess)

                if show_invalid_message:
                    self.draw_invalid_message(len(curr_guess_str) < GRID_COLS)

                pygame.display.flip()
                clock.tick(FPS)
            
            if game_won:
                return self.endscreen(curr_guess, answer_key, True, clock)  # Return restart decision
        
        if quit_game:
            return False  # Don't restart, user quit
        else:
            return self.endscreen(6, answer_key, False, clock)  # Return restart

# Run the game
if __name__ == "__main__":
    game = WordleGame()
    while True:
        if game.run_game():
            continue
        else:
            break

    pygame.quit()