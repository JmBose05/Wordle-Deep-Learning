import pygame

# pygame setup

def is_valid_answer(guess):
    return guess.lower() in valid_wordle_answer

def is_valid_guess(guess):
    return guess.lower() in valid_wordle_guess

def check_guess_against_answer(guess, answer, state, letters):
    #need matched_answer_indices because you cant match multiple letters in the guess to the same letter in answer 
    #e.g. if answer = BLACK, and guess = STALL, only one L should be yellow
    matched_answer_indices = set() 
    complete_match = True
    for index in range(5):
        if guess[index] != answer[index]:
            complete_match = False
            if guess[index] in answer:
                if answer.index(guess[index]) not in matched_answer_indices:
                    matched_answer_indices.add(answer.index(guess[index]))
                    state[index] = 'Yellow'
                else:
                    state[index] = 'Black'
            else:
                state[index] = 'Black'
        else: #direct match
            matched_answer_indices.add(index)
            state[index] = 'Green'
    return complete_match

#initialize sets
with open('valid_wordle_answer.txt', 'r') as answer_key_file:
    valid_wordle_answer = set(word.strip() for word in answer_key_file)
with open('valid_wordle_guess.txt', 'r') as guess_key_file:
    valid_wordle_guess = set(word.strip() for word in guess_key_file)

print("Enter the key: ")
while True:
    answer_key = input()
    if is_valid_answer(answer_key):
        print("Starting game!")
        break
    print("Invalid answer key...")
    print("Enter the key:")


pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
running = True
dt = 0

rect_width = 100
rect_height = 100
dist_between_rect = 15

all_rect_width = rect_width * 5 + dist_between_rect * 4
all_rect_height = rect_height * 6 + dist_between_rect * 5

dist_to_side_border = (screen.get_width() - all_rect_width)/ 2
dist_to_top_border = 100

pygame.display.set_caption("AI WORDLE PROJECT")
font = pygame.font.Font(None, 100)

title_surface = font.render("WORDLE", True, "black")
title_text = title_surface.get_rect()
title_text.center = (screen.get_width() // 2, dist_to_top_border // 2)


available_letters = {
    'A' : True, 'B' : True, 'C' : True, 'D' : True, 'E' : True, 'F' : True, 'G' : True, 'H' : True, 'I' : True,
    'J' : True, 'K' : True, 'L' : True, 'M' : True, 'N' : True, 'O' : True, 'P' : True, 'Q' : True, 'R' : True,
    'S' : True, 'T' : True, 'U' : True, 'V' : True, 'W' : True, 'X' : True, 'Y' : True, 'Z' : True,
}


game_grid_state =   [['Blank', 'Blank', 'Blank', 'Blank', 'Blank'],
                     ['Blank', 'Blank', 'Blank', 'Blank', 'Blank'],
                     ['Blank', 'Blank', 'Blank', 'Blank', 'Blank'],
                     ['Blank', 'Blank', 'Blank', 'Blank', 'Blank'],
                     ['Blank', 'Blank', 'Blank', 'Blank', 'Blank'],
                     ['Blank', 'Blank', 'Blank', 'Blank', 'Blank']]

game_grid_letters =   [['', '', '', '', ''],
                      ['', '', '', '', ''],
                      ['', '', '', '', ''],
                      ['', '', '', '', ''],
                      ['', '', '', '', ''],
                      ['', '', '', '', '']]

def draw_letters(letters, curr_guess):
    for row in range(curr_guess + 1):
        for col in range(5):
            x_rect_pos = dist_to_side_border + col*(dist_between_rect + rect_width)
            y_rect_pos = dist_to_top_border + row*(dist_between_rect + rect_height)

            tile_surface = font.render(game_grid_letters[row][col], True, "black")
            tile_rect =  tile_surface.get_rect()
            tile_rect.center = (x_rect_pos + (rect_width // 2), y_rect_pos + (rect_height // 2))

            screen.blit(tile_surface, tile_rect)

def draw_grid(state):
    all_green = True
    for row in range(6):
        for col in range(5):
            x_pos = dist_to_side_border + col*(dist_between_rect + rect_width)
            y_pos = dist_to_top_border + row*(dist_between_rect + rect_height)
            rect_color = state[row][col]
            if rect_color == 'Blank':
                pygame.draw.rect(screen, "black", (x_pos, y_pos, rect_width, rect_height), width=3)
                all_green = False
            elif rect_color == 'Black':
                pygame.draw.rect(screen, "grey", (x_pos, y_pos, rect_width, rect_height))
                all_green = False
            elif rect_color == 'Yellow':
                pygame.draw.rect(screen, "yellow", (x_pos, y_pos, rect_width, rect_height))
                all_green = False
            else:
                pygame.draw.rect(screen, "green", (x_pos, y_pos, rect_width, rect_height))

winscreen_width = 700
winscreen_height = 400
winscreen_x_pos = (screen.get_width() - winscreen_width) // 2
winscreen_y_pos = (screen.get_height() - winscreen_height) // 2

def winscreen(total_guesses, answer_key):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        #screen.fill("white")
        
        # Draw winscreen background
        pygame.draw.rect(screen, "lightgray", (winscreen_x_pos, winscreen_y_pos, winscreen_width, winscreen_height))
        pygame.draw.rect(screen, "black", (winscreen_x_pos, winscreen_y_pos, winscreen_width, winscreen_height), width=3)
        
        win_font = pygame.font.Font(None, 50)
    
        win_text1 = "Winner!"
        win_surface1 = win_font.render(win_text1, True, "black")
        win_rect1 = win_surface1.get_rect()
        win_rect1.center = (winscreen_x_pos + winscreen_width // 2, winscreen_y_pos + winscreen_height // 2 - 30)
        screen.blit(win_surface1, win_rect1)
        
        win_text2 = f"{total_guesses}/6 guesses used"
        win_surface2 = win_font.render(win_text2, True, "black")
        win_rect2 = win_surface2.get_rect()
        win_rect2.center = (winscreen_x_pos + winscreen_width // 2, winscreen_y_pos + winscreen_height // 2 + 30)
        screen.blit(win_surface2, win_rect2)
        
        answer_text = f"Answer: {answer_key.upper()}"
        answer_surface = win_font.render(answer_text, True, "black")
        answer_rect = answer_surface.get_rect()
        answer_rect.center = (winscreen_x_pos + winscreen_width // 2, winscreen_y_pos + winscreen_height // 2 + 80)
        screen.blit(answer_surface, answer_rect)
        
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

quit = False
game_won = False
for curr_guess in range(6):
    curr_guess_str = ''
    running = True

    show_invalid_message = False
    invalid_message_timer = 0
    invalid_message_duration = 2000

    while running:
        # poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                # Check for letters (a-z)
                if event.unicode.isalpha() and len(event.unicode) == 1:
                    letter = event.unicode.lower()
                    if len(curr_guess_str) < 5:
                        curr_guess_str += letter
                        game_grid_letters[curr_guess][len(curr_guess_str)-1] = letter
                # Check for Enter
                elif event.key == pygame.K_RETURN:
                    if len(curr_guess_str) == 5 and is_valid_guess(curr_guess_str):
                        running = False
                        if check_guess_against_answer(curr_guess_str, answer_key, game_grid_state[curr_guess], available_letters):
                            game_won = True
                            running = False
                        break
                    else:
                        show_invalid_message = True
                        invalid_message_timer = pygame.time.get_ticks()
                        
                # Check for Backspace
                elif event.key == pygame.K_BACKSPACE:
                    curr_guess_str = curr_guess_str [:-1]
                    game_grid_letters[curr_guess][len(curr_guess_str)] = ''
        
        if show_invalid_message:
            if pygame.time.get_ticks() - invalid_message_timer > invalid_message_duration:
                show_invalid_message = False

        screen.fill("white")
        screen.blit(title_surface, title_text)
       
        draw_grid(game_grid_state)
        draw_letters(game_grid_letters, curr_guess)

        if show_invalid_message:
            error_font = pygame.font.Font(None, 48)
            if len(curr_guess_str) < 5:
                error_text = "Need 5 letters!"
            else:
                error_text = "Invalid word!"
            error_surface = error_font.render(error_text, True, "red")
            error_rect = error_surface.get_rect()
            error_rect.center = (screen.get_width() // 2, dist_to_top_border // 2)

            padding = 20
            bg_rect = pygame.Rect(
                error_rect.x - padding,
                error_rect.y - padding,
                error_rect.width + 2 * padding,
                error_rect.height + 2 * padding
            )
            pygame.draw.rect(screen, "grey", bg_rect)
            pygame.draw.rect(screen, "black", bg_rect, width=2)  # Black border
            
            screen.blit(error_surface, error_rect)

        keys = pygame.key.get_pressed()
        

        # flip() the display to put your work on screen
        pygame.display.flip()
        clock.tick(60)
    if quit:
        pygame.quit()
    if game_won:
        winscreen(curr_guess, answer_key)

print("RAN OUT OF GUESSES, GAME OVER")
pygame.quit()