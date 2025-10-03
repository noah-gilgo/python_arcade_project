from PIL import Image

# Load and resize the image
img = Image.open("assets/textures/backgrounds/IMAGE_DEPTHS.png")
img = img.resize((int(540/2), int(408/2)), Image.NEAREST)  # NEAREST keeps pixels sharp

# Save or convert to Arcade texture
img.save("assets/textures/backgrounds/IMAGE_DEPTHS_lowres.png")
