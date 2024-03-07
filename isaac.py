import tkinter as tk
import math
import random
window = tk.Tk()
window.geometry("1920x1080")
orientations={87:(1,-1),#W
              65:(0,-1),#A
              83:(1,1),#S
              68:(0,1)}#D
arrows={
    37:(0,-1),#←
    38:(1,-1),#↑
    39:(0,1),#→
    40:(1,1)#↓
    
}
class player():
    def __init__(self):
        self.direction = [0,0]
        self.pos = [0,0]
        self.speed = 3
        self.tears=[]

        self.maxteartimer=50
        self.teartimer=0
        self.init_draw()
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

        print(self.teartimer)
        print(self.maxteartimer)
        if self.teartimer<self.maxteartimer:
            self.teartimer+=1


class Tear():
    def __init__(self):
        self.direction=[0,0]
        self.pos=Giova.pos.copy()
        self.speed=1 
        self.init_draw()
        self.timer=100
    def init_draw(self):
        self.tear_geometry = tk.Canvas(window,bg="red",height=10,width=10)
        self.tear_geometry.place(x=self.pos[0],y=self.pos[1])
        
    def update_state(self):
        
        self.die_check()
        if self.timer>0:
            self.pos = [self.pos[0]+self.direction[0]*self.speed,self.pos[1]+self.direction[1]*self.speed]
            self.tear_geometry.place(x=self.pos[0],y=self.pos[1])

    def die_check(self):
        self.timer-=1
        
        if self.timer<=0:
            Giova.tears.pop(0)
            self.tear_geometry.place_forget()
            self.tear_geometry.delete()

            #This might be needed but it makes it crash a lot more
            #self.tear_geometry.destroy()


            

Giova = player()


def input(event):
    pressed=event.keycode
    if pressed in orientations:
        rotate=orientations[pressed]
        Giova.direction[rotate[0]]=rotate[1]
        #print(f"updating state keycode:{pressed}, rotation {Giova.direction}")   
       
    elif pressed in arrows and Giova.teartimer==Giova.maxteartimer:
        Giova.teartimer=0
        new_tear=Tear()
        rotate=arrows[pressed]
        new_tear.direction[rotate[0]]=rotate[1]
        Giova.tears.append(new_tear)
def release(event):
    pressed=event.keycode
    if pressed in orientations:
        rotate=orientations[pressed]
        Giova.direction[rotate[0]]=0
        #print(f"Deleting state keycode:{pressed}, rotation {Giova.direction}")

def update():
    Giova.update_state()
    for single_tear in Giova.tears:
        single_tear.update_state()
    window.after(20,update)

update()
window.bind("<KeyPress>",input)
window.bind("<KeyRelease>",release)
window.mainloop()
