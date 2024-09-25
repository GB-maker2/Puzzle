import os
from PIL import Image, ImageOps

# Load the image
image_path = 'puzzle.png'
image = Image.open(image_path)

# Ensure the image is oriented correctly according to EXIF data
image = ImageOps.exif_transpose(image)

# Define the number of pieces
num_pieces = 84

# Calculate the size of each piece
piece_width = image.width // 12
piece_height = image.height // 7

# Create the output directory if it doesn't exist
output_dir = 'pieces'
os.makedirs(output_dir, exist_ok=True)

# Split the image and save each piece with their corresponding position name (row_col)
piece_counter = 0
for i in range(7):  # Rows
    for j in range(12):  # Columns
        if piece_counter >= num_pieces:
            break
        left = j * piece_width
        upper = i * piece_height
        right = left + piece_width
        lower = upper + piece_height
        piece = image.crop((left, upper, right, lower))
        piece_name = f"{i+1}_{j+1}"  # Naming pieces by row_col
        piece.save(os.path.join(output_dir, f'piece_{piece_name}.png'))
        piece_counter += 1
