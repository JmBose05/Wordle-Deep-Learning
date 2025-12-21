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

def get_validity_mask(dict_tensor, known_greens, known_greys, known_yellows):
    mask = torch.ones(dict_tensor.shape[0])
    for pos, letter_idx in known_greens:

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
    # answer encoded tensor (12972 x 5 x 26)
    guess_encoded_tensor = data['guess_tensor']
    # answer encoded tensor (2315 x 5 x 26)
    answer_encoded_tensor = data['answer_tensor']
    
    # CREATE GAME STATE VECT
    # represent the state of the game for input into the model to each guess
    # (# of total guesses in a round X # of char for each input X concatenated letter and game state representation)
    # (6 x 5 x 29)
    # first 26 values are the One-Hot letter encoding of one position on the board
    # the last 3 values are the One-Hot state encoding of one position on the board { incorrect, partially correct, correct}
    game_state_tensor = torch.zeros((6, 5, 29))


if __name__ == "__main__":
    main()
