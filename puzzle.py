import streamlit as st
from PIL import Image
import random
import json
import datetime

def refresh_page():
    st.rerun()

# Initialize session state
if 'puzzle_pieces' not in st.session_state:
    # Create a list of pieces in their correct positions
    st.session_state['puzzle_pieces'] = [{"url": f"pieces/piece_{i+1}_{j+1}.png", "unlocked": False} for i in range(7) for j in range(12)]
    # Unlock the first piece (corner piece)
    st.session_state['puzzle_pieces'][0]['unlocked'] = True

if 'unlock_order' not in st.session_state:
    # Shuffle the order of unlocking, but keeping the positions constant
    piece_indices = list(range(1, len(st.session_state['puzzle_pieces'])))  # Exclude the first piece
    random.shuffle(piece_indices)
    st.session_state['unlock_order'] = piece_indices

if 'attempts' not in st.session_state:
    st.session_state['attempts'] = 0

if 'unlocked_dates' not in st.session_state:
    st.session_state['unlocked_dates'] = []

if 'last_unlocked_piece' not in st.session_state:
    st.session_state['last_unlocked_piece'] = None

# Secret words dictionary
def load_secret_words(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Inicializa las palabras secretas
secret_words = load_secret_words('secret_words.json')

# Get today's date
today = datetime.datetime.now().date().strftime("%d/%m/%Y")

# Function to check the word and unlock a piece
def check_word(input_word, unlock_date):
    if st.session_state['attempts'] >= 3:
        return False, st.session_state['puzzle_pieces']
    
    if input_word.lower() == secret_words.get(unlock_date):
        # Unlock the next piece in the shuffled order
        next_piece_index = st.session_state['unlock_order'].pop(0)  # Get the next piece index
        st.session_state['puzzle_pieces'][next_piece_index]["unlocked"] = True
        st.session_state['unlocked_dates'].append(unlock_date)
        st.session_state['last_unlocked_piece'] = st.session_state['puzzle_pieces'][next_piece_index]["url"]  # Save the last unlocked piece
        st.session_state['attempts'] = 0  # Reset attempts
        return True, st.session_state['puzzle_pieces']
    else:
        st.session_state['attempts'] += 1

    return False, st.session_state['puzzle_pieces']

# Title of the app
st.title("Unlock the Puzzle Mahal!")

# Check if all pieces are unlocked
all_unlocked = all(piece["unlocked"] for piece in st.session_state['puzzle_pieces'])

if all_unlocked:
    # Show the complete image if all pieces are unlocked
    st.image('puzzle.png', use_column_width=True)
    st.success("Congratulations mahal ko! You've completed the puzzle!")
else:
    # Display the puzzle pieces (12x7 grid)
    cols = 12
    for i in range(7):
        cols_images = st.columns(cols)
        for j in range(cols):
            idx = i * cols + j
            if idx < len(st.session_state['puzzle_pieces']):
                piece = st.session_state['puzzle_pieces'][idx]
                if piece["unlocked"]:
                    cols_images[j].image(piece["url"], use_column_width=True)
                else:
                    # Display a specific placeholder for each locked piece
                    placeholder_path = f"pieces/placeholder_{idx + 1}.png"
                    cols_images[j].image(placeholder_path, use_column_width=True)

# Find the earliest date with locked pieces
unlock_date = min((date for date in secret_words.keys() if date not in st.session_state['unlocked_dates']), default=None)

if unlock_date and not all_unlocked:
    st.write(f"Unlock the piece from {unlock_date}:")
    input_word = st.text_input(f"Enter the secret word for {unlock_date}:")
    if st.button("Submit"):
        if st.session_state['attempts'] < 3:
            correct, updated_pieces = check_word(input_word, unlock_date)
            if correct:
                st.success("Correct! A new piece has been unlocked.")
                refresh_page()  # Refresca la página
            else:
                st.error(f"Incorrect word. You have {3 - st.session_state['attempts']} attempts left.")
        else:
            st.warning("No attempts left for today. Please try again tomorrow.")
elif all_unlocked:
    st.info("You got all the pieces!")
else:
    st.info("Great job today mahal! Come back tomorrow for more!")
