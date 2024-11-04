import streamlit as st
import json
import random
import datetime
import os

def refresh_page():
    st.rerun()

# Helper function to load secret words from a JSON file
def load_secret_words(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Set the path for progress.json in your repository
progress_file = 'progress.json'  # You can specify the full path here if needed

# Helper function to load saved state from a JSON file
def load_progress(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        # Initialize progress with default values
        return {
            "unlocked_dates": [],
            "last_unlocked_piece": None,
            "first_piece_unlocked": True,  # Start with the first piece unlocked
            "unlock_order": [],
            "piece_mapping": {}  # To map dates to specific pieces
        }

# Helper function to save progress to a JSON file
def save_progress(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Reset progress function
def reset_progress():
    # Reset to default values
    default_progress = {
        "unlocked_dates": [],
        "last_unlocked_piece": None,
        "first_piece_unlocked": True,  # Keep the first piece marked as unlocked
        "unlock_order": [],
        "piece_mapping": {}  # Clear piece mappings
    }
    save_progress(progress_file, default_progress)

# Initialize or load persistent data
progress_data = load_progress(progress_file)

# Load the dictionary of secret words from the JSON file
secret_words = load_secret_words('secret_words.json')

# Sort dates in chronological order (day/month/year format)
sorted_dates = sorted(secret_words.keys(), key=lambda date: datetime.datetime.strptime(date, "%m/%d/%Y"))

# Initialize session state
if 'puzzle_pieces' not in st.session_state:
    # Create a list of pieces in their correct positions
    st.session_state['puzzle_pieces'] = [{"url": f"pieces/piece_{i+1}_{j+1}.png", "unlocked": False} for i in range(7) for j in range(12)]

    # Unlock the first piece since it's always a given
    if progress_data["first_piece_unlocked"]:
        st.session_state['puzzle_pieces'][0]["unlocked"] = True  # Unlock the first piece

    # Unlock previously unlocked pieces based on saved progress
    for date in progress_data['unlocked_dates']:
        if date in progress_data.get('piece_mapping', {}):  # Use get to avoid KeyError
            idx = progress_data['piece_mapping'][date]  # Use piece mapping for the index
            st.session_state['puzzle_pieces'][idx]["unlocked"] = True

# Load unlocked dates into session state
if 'unlocked_dates' not in st.session_state:
    st.session_state['unlocked_dates'] = progress_data.get("unlocked_dates", [])

if 'last_unlocked_piece' not in st.session_state:
    st.session_state['last_unlocked_piece'] = progress_data.get("last_unlocked_piece", None)

# Set a randomized order for unlocking pieces if it's not already set
if 'unlock_order' not in st.session_state:
    if progress_data.get('unlock_order'):  # Use get to avoid KeyError
        st.session_state['unlock_order'] = progress_data['unlock_order']
    else:
        # Set a randomized order for unlocking the pieces, skipping the first piece
        remaining_indices = list(range(1, len(st.session_state['puzzle_pieces'])))
        random.shuffle(remaining_indices)
        st.session_state['unlock_order'] = remaining_indices

# Create a piece mapping if it doesn't exist
if 'piece_mapping' not in st.session_state:
    if progress_data.get('piece_mapping'):  # Use get to avoid KeyError
        st.session_state['piece_mapping'] = progress_data['piece_mapping']
    else:
        # Map dates to pieces randomly, skipping the first piece
        for date in sorted_dates:
            if len(st.session_state['piece_mapping']) < len(st.session_state['puzzle_pieces']) - 1:
                piece_index = st.session_state['unlock_order'].pop(0)  # Get the next random piece index
                st.session_state['piece_mapping'][date] = piece_index  # Map date to piece
        save_progress(progress_file, {
            "unlocked_dates": st.session_state['unlocked_dates'],
            "last_unlocked_piece": st.session_state['last_unlocked_piece'],
            "first_piece_unlocked": True,
            "unlock_order": st.session_state['unlock_order'],
            "piece_mapping": st.session_state['piece_mapping']
        })  # Save initial mapping

# Determine the next unlockable date
next_unlock_date = next((date for date in sorted_dates if date not in st.session_state['unlocked_dates']), None)

# Today's date
today = datetime.datetime.now().strftime("%m/%d/%Y")

# Function to check if the input word matches the secret word for a specific date
def check_word(input_word, unlock_date):
    if input_word.lower() == secret_words.get(unlock_date, "").lower():
        # Unlock the next piece in the random order
        if st.session_state['unlock_order']:
            next_piece_index = st.session_state['unlock_order'].pop(0)  # Get the next random piece index
            st.session_state['puzzle_pieces'][next_piece_index]["unlocked"] = True
            st.session_state['unlocked_dates'].append(unlock_date)  # Track unlocked date
            st.session_state['last_unlocked_piece'] = st.session_state['puzzle_pieces'][next_piece_index]["url"]

            # Save the updated progress
            save_progress(progress_file, {
                "unlocked_dates": st.session_state['unlocked_dates'],
                "last_unlocked_piece": st.session_state['last_unlocked_piece'],
                "first_piece_unlocked": True,  # Ensure first piece remains marked as unlocked
                "unlock_order": st.session_state['unlock_order'],  # Save the updated unlock order
                "piece_mapping": st.session_state['piece_mapping']  # Save the piece mapping
            })
        
            return True  # Indicate a successful unlock
    return False  # Incorrect word

# Title of the app
st.title("Unlock the Puzzle Mahal!")

# Check if all pieces are unlocked
all_unlocked = all(piece["unlocked"] for piece in st.session_state['puzzle_pieces'])

if next_unlock_date and not all_unlocked:
    # Check if the next unlockable date is today or earlier
    if datetime.datetime.strptime(next_unlock_date, "%m/%d/%Y") <= datetime.datetime.strptime(today, "%m/%d/%Y"):
        input_word = st.text_input(f"Enter the secret word for {next_unlock_date}:")
        if st.button("Submit"):
            if check_word(input_word, next_unlock_date):
                st.success("Correct! A new piece has been unlocked.")
                refresh_page()  # Refresh the page

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

# Add a button to reset progress
if st.button("Reset Progress"):
    reset_progress()
    st.success("Progress has been reset!")
    refresh_page()  # Refresh the page after resetting to reflect changes
