import tkinter as tk
import math
import random
window = tk.Tk()
window.geometry("1920x1080")
#A dictionary matching keycode with its direction
orientations={87:(1,-1),83:(1,1),65:(0,-1),68:(0,1)}

class player():
    def __init__(self):
        self.direction = [0,0]
        self.pos = [0,0]
        self.speed = 3
        self.init_draw()
        self.diagonal=False
    def init_draw(self):
        self.player_geometry = tk.Canvas(window,bg="blue",height=100,width=100)
        self.player_geometry.place(x=self.pos[0],y=self.pos[1])
    def update_state(self):
        #If going diagonally
        if self.direction[0]&self.direction[1]:
            self.pos = [self.pos[0]+self.direction[0]*self.speed*math.sqrt(2)/2,self.pos[1]+self.direction[1]*self.speed*math.sqrt(2)/2]
        else:
            self.pos = [self.pos[0]+self.direction[0]*self.speed,self.pos[1]+self.direction[1]*self.speed]
        self.player_geometry.place(x=self.pos[0],y=self.pos[1])
        

Giova = player()

def input(event):
    if event.keycode in orientations:
        rotate=orientations[event.keycode]
        Giova.direction[rotate[0]]=rotate[1]
        print(f"updating state keycode:{event.keycode}, rotation {Giova.direction}")
        
        #Giova.update_state()
        
def release(event):
    if event.keycode in orientations:
        rotate=orientations[event.keycode]
        Giova.direction[rotate[0]]=0
        print(f"Deleting state keycode:{event.keycode}, rotation {Giova.direction}")


def update():
    Giova.update_state()
    window.after(20,update)

update()
window.bind("<KeyPress>",input)
window.bind("<KeyRelease>",release)
window.mainloop()
