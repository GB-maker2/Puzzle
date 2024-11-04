import streamlit as st
import json
import datetime
import os

def refresh_page():
    st.rerun()

# Helper function to load secret words from a JSON file
def load_secret_words(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Helper function to load saved state from a JSON file
def load_progress(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        return {"unlocked_dates": [], "last_unlocked_piece": None}

# Helper function to save progress to a JSON file
def save_progress(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Initialize or load persistent data
progress_file = 'progress.json'
progress_data = load_progress(progress_file)

# Initialize session state
if 'puzzle_pieces' not in st.session_state:
    # Create a list of pieces in their correct positions
    st.session_state['puzzle_pieces'] = [{"url": f"pieces/piece_{i+1}_{j+1}.png", "unlocked": False} for i in range(7) for j in range(12)]
    
    # Unlock previously unlocked pieces based on saved progress
    for date in progress_data['unlocked_dates']:
        idx = progress_data['unlocked_dates'].index(date)
        st.session_state['puzzle_pieces'][idx]["unlocked"] = True

if 'unlocked_dates' not in st.session_state:
    # Use the saved unlocked dates from the progress file
    st.session_state['unlocked_dates'] = progress_data.get("unlocked_dates", [])

if 'last_unlocked_piece' not in st.session_state:
    st.session_state['last_unlocked_piece'] = progress_data.get("last_unlocked_piece", None)

# Load the dictionary of secret words from the JSON file
secret_words = load_secret_words('secret_words.json')

# Sort dates in chronological order
sorted_dates = sorted(secret_words.keys(), key=lambda date: datetime.datetime.strptime(date, "%d/%m/%Y"))

# Determine the next unlockable date
next_unlock_date = next((date for date in sorted_dates if date not in st.session_state['unlocked_dates']), None)

# Today's date
today = datetime.datetime.now().strftime("%d/%m/%Y")

# Function to check if the input word matches the secret word for a specific date
def check_word(input_word, unlock_date):
    if input_word.lower() == secret_words.get(unlock_date, "").lower():
        # Unlock the next piece
        next_piece_index = len(st.session_state['unlocked_dates'])  # Get the next piece index in order
        st.session_state['puzzle_pieces'][next_piece_index]["unlocked"] = True
        st.session_state['unlocked_dates'].append(unlock_date)  # Track unlocked date
        st.session_state['last_unlocked_piece'] = st.session_state['puzzle_pieces'][next_piece_index]["url"]
        
        # Save the updated progress
        save_progress(progress_file, {
            "unlocked_dates": st.session_state['unlocked_dates'],
            "last_unlocked_piece": st.session_state['last_unlocked_piece']
        })
        
        return True  # Indicate a successful unlock
    return False  # Incorrect word

# Title of the app
st.title("Unlock the Puzzle Mahal!")

# Check if all pieces are unlocked
all_unlocked = all(piece["unlocked"] for piece in st.session_state['puzzle_pieces'])

if next_unlock_date and not all_unlocked:
    # Check if the next unlockable date is today or earlier
    if datetime.datetime.strptime(next_unlock_date, "%d/%m/%Y") <= datetime.datetime.strptime(today, "%d/%m/%Y"):
        st.write(f"Unlock the piece from {next_unlock_date}:")
        input_word = st.text_input(f"Enter the secret word for {next_unlock_date}:")
        if st.button("Submit"):
            if check_word(input_word, next_unlock_date):
                st.success("Correct! A new piece has been unlocked.")
                refresh_page()  # Refresh the page
            else:
                st.error("Incorrect word. Please try again.")
    else:
        st.info("Great job today mahal! Come back tomorrow for more!")
else:
    st.info("Great job today mahal! Come back tomorrow for more!")

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
