# placeholder.py
from PIL import Image

# Create a new blank placeholder image (e.g., 100x100 pixels)
width, height = 100, 100
placeholder_image = Image.new("RGB", (width, height), color="gray")

# Optionally add text to the placeholder image
from PIL import ImageDraw, ImageFont

draw = ImageDraw.Draw(placeholder_image)
font = ImageFont.load_default()
draw.text((10, 40), "Locked", fill="white", font=font)

# Save 84 placeholder images
for i in range(1, 85):
    placeholder_image.save(f"pieces/placeholder_{i}.png")
