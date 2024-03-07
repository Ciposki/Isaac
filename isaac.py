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
def detect_collision(a,b):
    """
    IF A IS INSIDE B
    """ 
    if ((b.pos[0]<=a.pos[0]<=b.pos[0]+b.xbound) or (b.pos[0]<=a.pos[0]+a.xbound<=b.pos[0]+b.xbound)) and ((b.pos[1]<=a.pos[1]<=b.pos[1]+b.ybound) or (b.pos[1]<=a.pos[1]+a.ybound<=b.pos[1]+b.ybound)):
        return True
    return False

class player():
    def __init__(self):
        self.direction = [0,0]
        self.pos = [0,0]
        self.speed = 3
        self.tears=[]
        self.hp=6
        self.maxteartimer=50
        self.teartimer=0
        self.ybound=100
        self.xbound=100
        self.invincibility_timer=0
        self.maxinvincibility_timer=21
        
        self.init_draw()
    def init_draw(self):
        self.player_geometry = tk.Canvas(window,bg="blue",height=self.ybound,width=self.xbound)
        self.player_geometry.place(x=self.pos[0],y=self.pos[1])
    def update_state(self):
        #If going diagonally
        oldpos=self.pos.copy()
        if self.direction[0]&self.direction[1]:
            self.pos = [self.pos[0]+self.direction[0]*self.speed*math.sqrt(2)/2,self.pos[1]+self.direction[1]*self.speed*math.sqrt(2)/2]
        else:
            self.pos = [self.pos[0]+self.direction[0]*self.speed,self.pos[1]+self.direction[1]*self.speed]
        self.player_geometry.place(x=self.pos[0],y=self.pos[1])
        if self.teartimer<self.maxteartimer:
            self.teartimer+=1
        if self.detect_collisions()==2:
            self.pos=oldpos
            
        """
        THIS COULD PROBABLY BE DONE IN A CLEANER WAY
        """
        if self.invincibility_timer==20:
            self.invincibility_timer=0
        if self.invincibility_timer>0:
            self.invincibility_timer+=1
    def detect_collisions(self):
        
        
        for enemy in enemies:
            if detect_collision(self,enemy):
                self.take_damage(1)
                return 2
        for object in environment:
            if detect_collision(self,object):
                return 2
        for tear in enemy_tears:
            if detect_collision(tear,self):
                self.take_damage(1)
                tear.die()
                return 1
        return 0
    def take_damage(self,damage):
        if self.invincibility_timer==0:
            if self.hp==0:
                print("GAY")
            else:
                self.hp-=damage
                self.invincibility_timer=1
class Tear():
    def __init__(self):
        self.direction=[0,0]
        self.pos=Giova.pos.copy()
        self.speed=4
        self.timer=100
        self.xbound=10
        self.ybound=10
        self.init_draw()

    def init_draw(self):
        self.tear_geometry = tk.Canvas(window,bg="green",height=self.ybound,width=self.xbound)
        self.tear_geometry.place(x=self.pos[0],y=self.pos[1])
        
    def update_state(self):
        self.timer-=1
        if self.timer<=0:
            self.die()
        else:
            self.pos = [self.pos[0]+self.direction[0]*self.speed,self.pos[1]+self.direction[1]*self.speed]
            self.tear_geometry.place(x=self.pos[0],y=self.pos[1])
            for obj in environment:
                if detect_collision(self,obj):
                    self.die()

    def die(self):
        
            Giova.tears.remove(self)
            self.tear_geometry.place_forget()
            self.tear_geometry.delete()
            self.tear_geometry.destroy()


"""THIS COULD BE CLEANED UP WITH INHERITANCE"""
class Enemy_Tear():
    def __init__(self):
        self.direction=[0,0]
        self.pos=[0,0]
        self.speed=1 
        self.timer=100
        self.xbound=10
        self.ybound=10
        self.init_draw()

    def init_draw(self):
        self.tear_geometry = tk.Canvas(window,bg="purple",height=self.ybound,width=self.xbound)
        
    def update_state(self):
        self.timer-=1
        if self.timer<=0:
            self.die()
        else:
            self.pos = [self.pos[0]+self.direction[0]*self.speed,self.pos[1]+self.direction[1]*self.speed]
            self.tear_geometry.place(x=self.pos[0],y=self.pos[1])
            for obj in environment:
                if detect_collision(self,obj):
                    self.die()
    def die(self):
        
            enemy_tears.pop(0)
            self.tear_geometry.place_forget()
            self.tear_geometry.delete()
            self.tear_geometry.destroy()




class Static_Enemy():
    def __init__(self):
        self.direction=[0,0]
        self.pos=[300,350]
        self.ybound=100
        self.xbound=100
        self.timer=100
        self.timerdefault=100
        self.hp=4
        self.init_draw()
        
    def init_draw(self):
        self.enemy_geometry = tk.Canvas(window,bg="red",height=self.ybound,width=self.xbound)
        self.enemy_geometry.place(x=self.pos[0],y=self.pos[1])
    def update_state(self):
        if self.hp<=0:
            self.die()
        else:
            self.detect_collisions()
            self.timer-=1
            if self.timer==0:
                newtear=Enemy_Tear()
                newtear.pos=[300,350]
                newtear.direction=[0,-1]
                enemy_tears.append(newtear)
                
                
                self.timer=self.timerdefault
        
    def detect_collisions(self):
        for tear in Giova.tears:
            xtear=tear.pos[0]
            ytear=tear.pos[1]
            if detect_collision(tear,self):
                self.hp-=1
                tear.die()
                break
    def die(self):
        enemies.remove(self)
        self.enemy_geometry.place_forget()
        self.enemy_geometry.delete()
        self.enemy_geometry.destroy()

class Wall():
    def __init__(self):
        self.pos=[500,500]
        self.ybound=100
        self.xbound=100
        self.enemy_geometry = tk.Canvas(window,bg="black",height=100,width=100)
        self.enemy_geometry.place(x=self.pos[0],y=self.pos[1])

Giova = player()
enemies=[Static_Enemy()]
enemy_tears=[]
environment=[Wall()]
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
    for enemy in enemies:
        enemy.update_state()
    for enemy_tear in enemy_tears:
        enemy_tear.update_state()
    window.after(20,update)

update()
window.bind("<KeyPress>",input)
window.bind("<KeyRelease>",release)
window.mainloop()