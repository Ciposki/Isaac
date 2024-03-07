import tkinter as tk
import math
import random


window = tk.Tk()
window.geometry("1920x1080")

var = tk.StringVar()
history=[]

class player():
    def __init__(self):
        self.direction = [0,0]
        self.pos = [0,0]
        self.speed = 3
        self.init_draw()
    def init_draw(self):
        self.player_geometry = tk.Canvas(window,bg="blue",height=100,width=100)
        self.player_geometry.place(x=self.pos[0],y=self.pos[1])
    def update_state(self):
        
        for i in history:
            match i:
                case 87:
                    self.direction[1]=-1
                case 83:
                    self.direction[1]=1
                case 65:
                    self.direction[0]=-1
                case 68:
                    self.direction[0]=1
                case _:
                    self.direction = [0,0]
        print(self.direction)
        self.pos = [self.pos[0]+self.direction[0]*self.speed,self.pos[1]+self.direction[1]*self.speed]
        self.player_geometry.place(x=self.pos[0],y=self.pos[1])

Giova = player()

def input(event):
    if not event.keycode in history and event.keycode in [87,65,83,68] :
        history.append(event.keycode)
        var.set(str(history))
    Giova.update_state()
        
def release(event):
    if  event.keycode in history :
        history.pop(history.index(event.keycode))
        Giova.direction = [0,0]
        var.set(str(history))


window.bind("<KeyPress>",input)
window.bind("<KeyRelease>",release)
window.mainloop()