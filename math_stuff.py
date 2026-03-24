import numpy as np
import torch
import torch.nn as nn
import random
import time
import matplotlib.pyplot as plt

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'

class WordlePolicy(nn.Module):
    def __init__(self, dict_size):
        super(WordlePolicy, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(dict_size, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, dict_size) # Output logits for every word
        )

    def forward(self, mask):
        return self.network(mask)  

def get_feedback(guess_encoded, answer_encoded):
    """
    Inputs:
        guess_encoded: (5 x 26) tensor (one-hot)
        answer_encoded: (5 x 26) tensor (one-hot)
    Returns:
        greens: list of (position, letter_index)
        yellows: list of (position, letter_index)
        greys: list of letter_index
    """
    # convert one-hot encoding to index (e.g. [2, 17, 0, 13, 4] for crane)
    guess_idxs = torch.argmax(guess_encoded, dim=1)
    answer_idxs = torch.argmax(answer_encoded, dim=1)

    greens = []
    yellows = []
    greys = set() # set to avoid dupes

    # track which letters in the answer are consumed for yellow clues
    # this prevents marking two of the same letter yellow if only one exists in the answer
    answer_flags = [False] * 5
    guess_flags = [False] * 5

    # find the greens:
    for i in range(5):
        if guess_idxs[i] == answer_idxs[i]:
            greens.append((i, guess_idxs[i]))
            answer_flags[i] = True
            guess_flags[i] = True
    
    # find the yellows:
    for i in range(5):
        if guess_flags[i]: continue # skip if already green

        for j in range(5):
            if not answer_flags[j] and guess_idxs[i] == answer_idxs[j]:
                yellows.append((i, guess_idxs[i].item()))
                answer_flags[j] = True
                guess_flags[i] = True
                break

    # find the greys (only if not yellow or green)
    all_known_active = [g[1] for g in greens] + [y[1] for y in yellows]
    
    for i in range(5):
        char_idx = guess_idxs[i].item()
        if not guess_flags[i] and char_idx not in all_known_active:
            greys.add(char_idx)

    return greens, yellows, list(greys)

def get_validity_mask(dict_tensor, known_greens, known_greys, known_yellows):
    """
    Inputs: 
        dict_tensor: (12,972 x 5 x 26) tensor of all valid guesses
        known_greens:  list of (pos, idx) representing green letters
        known_greys: list of letter_idx representing grey letters 
        known_yellows: list of (pos, idx) representing yellow letters
    Returns:
        validity_mask: (12,972 x 1) tensor of all remaining 'valid' guesses
    """
    num_words = dict_tensor.shape[0]
    device = dict_tensor.device
    # All words are valid (1), mask (12972 x 1)
    mask = torch.ones(num_words, dtype=torch.bool, device=dict_tensor.device)
    
    # 1. Check greens
    for pos, letter_idx in known_greens:
        mask &= (dict_tensor[:, pos, letter_idx] == 1)

    # Check yellows
    for pos, letter_idx in known_yellows:
        # Must contain the letter AND not be at the specific position
        has_letter = dict_tensor[:, :, letter_idx].any(dim=1)
        not_at_pos = (dict_tensor[:, pos, letter_idx] == 0)
        mask &= (has_letter & not_at_pos)

    # 3. Check greys
    if known_greys:
        # Sum across the alphabet dimension for just the grey indices
        grey_indices = torch.tensor(known_greys, device=device)
        # Any word containing any of these letters becomes False
        has_any_grey = dict_tensor[:, :, grey_indices].any(dim=(1, 2))
        mask &= ~has_any_grey

    return mask.float()

def masked_softmax(logits, mask, temperature=1.0):
    mask_inf = (1.0 - mask) * -1e9
    masked_logits = (logits + mask_inf) / temperature
    return torch.softmax(masked_logits, dim=0)          

def compute_reward(turns_taken, won):
    if not won:
        return 0.0
    # Reward is higher for fewer turns (1.0 for 1 turn, 0.16 for 6 turns)
    return 1.0 / turns_taken

def train_one_episode(model, optimizer, guess_tensor, answer_tensor, device):
    target_idx = random.randrange(len(answer_tensor))
    target_word = answer_tensor[target_idx]
    
    mask = torch.ones(guess_tensor.shape[0], device=device)
    log_probs = []
    won = False
    turns_taken = 0
    
    for turn in range(6):
        turns_taken += 1
        logits = model(mask)
        probs = masked_softmax(logits, mask)
        
        # Categorical distribution for sampling and log_probs
        m = torch.distributions.Categorical(probs)
        guess_idx = m.sample()
        log_probs.append(m.log_prob(guess_idx))
        
        if guess_idx.item() == target_idx: # Direct comparison for win
            won = True
            break
            
        # Feedback and state update
        greens, yellows, greys = get_feedback(guess_tensor[guess_idx], target_word)
        new_constraints = get_validity_mask(guess_tensor, greens, greys, yellows)
        mask = mask * new_constraints
        mask = mask.clone()
        mask[guess_idx] = 0

    
    reward = compute_reward(turns_taken, won)
    
    # Policy Gradient optimization
    policy_loss = [-lp * reward for lp in log_probs]
    optimizer.zero_grad()
    sum(policy_loss).backward()
    optimizer.step()
    
    return reward, turns_taken

def load_and_encode(file_path):
    """
    Inputs: 
        file_path of .txt file containing words (len(words) x char/word)
    Returns:
        encoded_tensor: (len(words) x char/word x 26) tensor of the words
        words: one hot encoding of the words
    """
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

def play_game(model, guess_tensor, answer_tensor, guess_words, device):
    model.eval() # Set to evaluation mode
    
    # Pick a random answer
    target_idx = random.randrange(len(answer_tensor))
    target_word = answer_tensor[target_idx]
    target_str = guess_words[target_idx]
    
    # Initialize the state
    mask = torch.ones(guess_tensor.shape[0], device=device)
    print(f"\n--- Target Word: {target_str.upper()} ---")
    
    with torch.no_grad(): # Disable gradient tracking for performance
        for turn in range(1, 7):
            valid_count = int(torch.sum(mask).item())

            logits = model(mask)
            # Use argmax to see the model's "absolute best" guess
            probs = masked_softmax(logits, mask)
            guess_idx = torch.argmax(probs).item()
            guess_str = guess_words[guess_idx]
            
            print(f"Turn {turn}: Model guessed '{guess_str.upper()}' | {valid_count} words remaining.")

            if guess_idx == target_idx:
                print(f"The model won in {turn} turns.")
                return
                
            # Get feedback and update the mask
            greens, yellows, greys = get_feedback(guess_tensor[guess_idx], target_word)
            new_constraints = get_validity_mask(guess_tensor, greens, greys, yellows)
            mask = mask * new_constraints
            mask = mask.clone()
            mask[guess_idx] = 0
            
    print(f"The model failed to find {target_str.upper()}.")

def evaluate_model(model, guess_tensor, answer_tensor, device, num_games=50):
    model.eval()
    total_turns = 0
    wins = 0
    
    with torch.no_grad():
        for _ in range(num_games):
            # Pick a target from the answer list
            target_idx = random.randrange(len(answer_tensor))
            target_word = answer_tensor[target_idx]
            
            mask = torch.ones(guess_tensor.shape[0], device=device)
            
            for turn in range(1, 7):
                logits = model(mask)
                # Use T=0.1 or argmax for "best" behavior during eval
                probs = masked_softmax(logits, mask, temperature=0.1) 
                guess_idx = torch.argmax(probs).item()
                
                if guess_idx == target_idx:
                    wins += 1
                    total_turns += turn
                    break
                
                # Feedback and Persistent Mask Update
                greens, yellows, greys = get_feedback(guess_tensor[guess_idx], target_word)
                new_constraints = get_validity_mask(guess_tensor, greens, greys, yellows)
                mask = (mask * new_constraints).clone()
                mask[guess_idx] = 0
                
    avg_turns = total_turns / wins if wins > 0 else 6.0
    win_rate = (wins / num_games) * 100
    return avg_turns, win_rate

def plot_training_results(stats_history):
    epochs = stats_history["epoch"]
    win_rates = stats_history["win_rate"]
    avg_rewards = stats_history["avg_reward"]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot Win Rate
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Win Rate (%)', color='tab:blue')
    ax1.plot(epochs, win_rates, color='tab:blue', label='Win Rate', linewidth=2)
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Create a second y-axis for Average Reward
    ax2 = ax1.twinx()
    ax2.set_ylabel('Avg Reward (1/Turns)', color='tab:red')
    ax2.plot(epochs, avg_rewards, color='tab:red', label='Avg Reward', linestyle='--')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    plt.title('Wordle Agent Training Progress')
    fig.tight_layout()
    plt.savefig('training_performance.png')
    print("\nPerformance graph saved as 'training_performance.png'")

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    data = np.load('wordle_data.npz')
    
    guess_tensor = torch.from_numpy(data['guess_tensor']).float().to(device)
    answer_tensor = torch.from_numpy(data['answer_tensor']).float().to(device)
    
    guess_words = data['guess_words']

    model = WordlePolicy(dict_size=len(guess_words)).to(device)
    model.load_state_dict(torch.load("wordle_model.pth"))
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    running_reward = 0
    running_wins = 0
    stats_history = {
        "epoch": [],
        "avg_reward": [],
        "win_rate": []
    }
    best_openers_history = []
    current_best_word = None

    print("Starting training...")
    for epoch in range(1, 10001):
        model.train()
        
        reward, turns = train_one_episode(model, optimizer, guess_tensor, answer_tensor, device)
        running_reward += reward
        if reward > 0:
            running_wins += 1
        
        if epoch % 100 == 0:
            with torch.no_grad():
                initial_mask = torch.ones(len(guess_words), device=device)
                best_idx = torch.argmax(model(torch.ones(len(guess_words), device=device))).item()
                best_word = guess_words[best_idx]

                if best_word != current_best_word:
                    best_openers_history.append((epoch, best_word))
                    current_best_word = best_word

            print(f"Epoch {epoch} | Best Opener: {best_word}")

            avg_reward = running_reward / 100
            win_rate = (running_wins / 100) * 100
            
            # Store for the final report
            stats_history["epoch"].append(epoch)
            stats_history["avg_reward"].append(avg_reward)
            stats_history["win_rate"].append(win_rate)
            
            # Reset accumulators
            running_reward = 0
            running_wins = 0

    print("\n" + "="*35)
    print(f"{'Epoch':<10} | {'Win Rate':<10} | {'Avg Reward':<10}")
    print("-" * 35)
    for i in range(len(stats_history["epoch"])):
        print(f"{stats_history['epoch'][i]:<10} | "
              f"{stats_history['win_rate'][i]:<9.1f}% | "
              f"{stats_history['avg_reward'][i]:<10.4f}")
    
    print("\n" + "="*35)
    print("   STRATEGY EVOLUTION LOG")
    print("="*35)
    for epoch, word in best_openers_history:
        print(f"Epoch {epoch:4d}: {word.upper()}")
    print("="*35)

    # Identify the Final Best Opener
    with torch.no_grad():
        model.eval()
        initial_mask = torch.ones(len(guess_words), device=device)
        final_opener_idx = torch.argmax(model(initial_mask)).item()
        print("-" * 35)
        print(f"Final Optimal Opener: {guess_words[final_opener_idx].upper()}")
        print("="*35)

    # Generate the Graph
    plot_training_results(stats_history)

    torch.save(model.state_dict(), "wordle_model.pth")

if __name__ == "__main__":
    main()
