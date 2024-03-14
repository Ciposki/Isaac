from tkinter import *
from PIL import Image


root = Tk()
root.title("Game")


frame = Frame(root)
frame.pack()


canvas = Canvas(frame, bg="black", width=700, height=400)
canvas.pack()


background = PhotoImage(file="room0.png")
canvas.create_image(350,200,image=background)

character = PhotoImage(file="front.png")
ch2 = PhotoImage(file="back.png")
if 1:
    i=canvas.create_image(100,30,image=character)
    i=canvas.create_image(100,30,image=ch2)
root.mainloop()