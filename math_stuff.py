import numpy as np
import torch
import random

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'


# input: .txt file containing words (len(words) x char/word)
# output: encoded tensor of of the words (len(words) x char/word x 26)
# one hot encoding of letter is 1 x 26 vector with 1 corresponding to index in the alphabet
def load_and_encode(file_path):
    with open(file_path, 'r') as f:
        #load words and strip whitepsace
        # words = (len(words) x num char)
        words = [line.strip().lower() for line in f.readlines()]

    # empty tensor (Number of valid guesses x 5 positions x 26 letters)
    encoded_tensor = torch.zeros((len(words), 5, 26))

    ALPHABET = "abcdefghijklmnopqrstuvwxyz"

    # position if position X, Y, Z = 1:
    # the row(X-axis) represents the position of the word in the dictionary
    # the column(Y-axis) represents the position of the character in character in the word
    # the depth(Z-axis) represents the letter of the alphabet
    for word_idx, word in enumerate(words):
        for char_idx, char in enumerate(word):
            letter_idx = ALPHABET.index(char)
            encoded_tensor[word_idx, char_idx, letter_idx] = 1

    return encoded_tensor, words

def pick_random_key(answer_encoded_tensor):
    # pick from key in the answers encoded tensor
    # range 0 to len(answer_encoded_tensor) - 1
    return random.randrange(len(answer_encoded_tensor))

# input: 5 x 26 word represented by the one hot encodings
def decode_word(word):
    # list of idx where value = '1' in each of the rows of the word
    idx = np.argmax(word, axis=1)
    # reconstruct word
    decoded_word = "".join([ALPHABET[i] for i in idx])

    return decoded_word

# input:    dict_tensor (12,972 x 5 x 26) - the dictionary of all valid guesses
#           known_greens -  list of tuples representing green letters and
#                           their corresponding indexes - (2,0) - C is green at idx 0
#           known_greys -   list of integers representing the letters that are known 
#                           to be grey - [0,1,5] - A, B, & E are known greys
#           ***letters will only be present in known_greys if they are not already marked 
#              as green or yellow to handle the double letter edge case***
#           known_yellows - list of ints corresponding to the known yellow letters

def get_validity_mask(dict_tensor, known_greens, known_greys, known_yellows):
    # All words are valid (1), mask (12972 x 1)
    mask = torch.ones(dict_tensor.shape[0], dtype=torch.float32)
    
    # Green loop: modify the mask with all of the known green letter positions
    for pos, letter_idx in known_greens:
        # for every <position, letter> pair, filter out words that do not match
        mask *= (dict_tensor[:, pos, letter_idx])
    
    for pos, letter_id in known_yellows:
        # remaining valid words must contain the yellow letter and not be at the same position 
        word_has_letter = (dict_tensor[:, :, letter_idx].sum(dim=1) > 0).float()
        not_at_curr_pos = (dict_tensor[:, pos, letter_idx] == 0)

        mark *= (word_has_letter & not_at_curr_pos).float() 

    # Grey loop: modify the mask with all of the known grey letters
    for letter_idx in known_greys:
        # if the word contains the grey letter, it is invalid
        word_has_letter = dict_tensor[:, :, letter_idx].sum(dim=1)
        mask *= (word_has_letter == 0).float()

    return mask

def main():
    # CREATE ENCODED TENSOR AND SAVE IT
    # 1 for both the list of possible guesses and list of possible answers
    
    # guess_encoded_tensor_pt, guess_words = load_and_encode('./valid_wordle_guess.txt')
    # answer_encoded_tensor_pt, answer_words = load_and_encode('./valid_wordle_answer.txt')
    
    # np.savez_compressed('wordle_data.npz', 
    #                     guess_words=guess_words,
    #                     answer_words=answer_words, 
    #                     guess_tensor=guess_encoded_tensor_pt.numpy(), 
    #                     answer_tensor=answer_encoded_tensor_pt.numpy())
    
    data = np.load('wordle_data.npz')
    guess_words = data['guess_words']
    answer_words = data['answer_words']
    # answer encoded tensor (12,972 x 5 x 26)
    guess_encoded_tensor = data['guess_tensor']
    # answer encoded tensor (2,315 x 5 x 26)
    answer_encoded_tensor = data['answer_tensor']
    
    # CREATE GAME STATE VECT
    # represent the state of the game for input into the model to make each guess
    # (# of total guesses in a round X # of char for each input X concatenated letter and game state representation)
    # (6 x 5 x 29)
    # first 26 values are the One-Hot letter encoding of one position on the board
    # the last 3 values are the One-Hot state encoding of one position on the board { incorrect, partially correct, correct}
    game_state_tensor = torch.zeros((6, 5, 29))


if __name__ == "__main__":
    main()
