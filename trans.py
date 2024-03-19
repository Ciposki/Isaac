import tkinter as tk
from PIL import Image, ImageTk

def move_image(event):
    # Move the image right and down for demonstration. Adjust as needed.
    canvas.move(image_id, 10, 10)
    canvas.update()

# Create the main window
root = tk.Tk()
root.geometry('800x600')

# Load the background image
bg_image = Image.open('back.png')
bg_photo = ImageTk.PhotoImage(bg_image)

# Create a canvas and add the background image
canvas = tk.Canvas(root, width=800, height=600)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor='nw')

# Load the transparent image
trans_image = Image.open('front.png')

# Resize the transparent image (adjust the size as needed)
trans_image_resized = trans_image.resize((100, 100))  # Example size: 100x100 pixels

trans_photo = ImageTk.PhotoImage(trans_image_resized)

# Place the resized transparent image on the canvas
image_id = canvas.create_image(100, 100, image=trans_photo, anchor='nw')

# Bind key or button event to move the image
root.bind('<Right>', move_image)  # Moves the image on pressing the right arrow key

head_img=ImageTk.PhotoImage(Image.open("room0.png").resize((100,100)))
head_id=canvas.create_image(100,100,image=head_img)
#canvas.tag_raise(head_id)
canvas.tag_lower(head_id)

root.mainloop()
