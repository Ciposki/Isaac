#TODO Fix Input(you cant move and shoot at the same time)
# Random enemy collisions are broken

import tkinter as tk
import math
import random
import sys
from PIL import ImageTk, Image



random_dir=[-1,-0.5,0,1,0.5]
window = tk.Tk()
window.iconphoto(True,ImageTk.PhotoImage(Image.open("Isaac.png")))
window.title("The Binding of Giovanni")
width=1920
height=1080
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
directions=[(0,1),(1,0),(0,-1),(-1,0)]
door_positions=([width/2,0],[0,height/2],[width/2,height],[width,height/2])

def kill_enemy(object):
    if random.randint(10,10)==10:
        coin=Coin()
        coin.pos=object.pos
        world.currentroom.coins.append(coin)
        coin.update()
    world.currentroom.enemies.remove(object)
    object.enemy_geometry.place_forget()
    object.enemy_geometry.delete()
    object.enemy_geometry.destroy()

def normalize_vector(vector):
    magnitude = sum(i**2 for i in vector)**0.5
    return [i/magnitude for i in vector]

def detect_collision(a,b):
    """
    IF A IS INSIDE B
    """ 
    if ((b.pos[0]<=a.pos[0]<=b.pos[0]+b.xbound) or (b.pos[0]<=a.pos[0]+a.xbound<=b.pos[0]+b.xbound)) and ((b.pos[1]<=a.pos[1]<=b.pos[1]+b.ybound) or (b.pos[1]<=a.pos[1]+a.ybound<=b.pos[1]+b.ybound)):
        return True
    return False

def spawn_tear(direction,tear,entity):
    """Spawns a tear based on the direction"""
    tear.pos=entity.pos.copy()
    tear.direction[arrows[direction][0]]=arrows[direction][1]
    match direction:
        case 37:
            tear.pos[1]+=(entity.ybound)/2
        case 38:
            tear.pos[0]+=(entity.xbound)/2
        case 39:
            tear.pos[1]+=(entity.ybound)/2
            tear.pos[0]+=(entity.xbound)
        case 40:
            tear.pos[0]+=(entity.xbound)/2
            tear.pos[1]+=(entity.ybound)

def enemy_collisions(self):
    for tear in Giova.tears:
            if detect_collision(tear,self):
                self.hp-=Giova.damage
                tear.die()
                return 1
    for tear in world.currentroom.enemy_tears:
        if detect_collision(tear,self):
            tear.die()
            return 1
    if detect_collision(Giova,self):
        return 2
    

    for object in world.currentroom.environment:
        if detect_collision(object,self):
            return 2
    for enemy in world.currentroom.enemies:
        if enemy!=self and detect_collision(enemy,self):
            return 2
        
def rotate(self,deg):
        match deg:
            case 0:
                self.pos[0]-=self.xbound/2
            case 1:
                self.xbound,self.ybound=self.ybound,self.xbound
                self.pos[1]-=self.ybound/2
            case 2:
                self.pos[1]-=self.ybound
                self.pos[0]-=self.xbound/2
            case 3:
                self.xbound,self.ybound=self.ybound,self.xbound
                self.pos[0]-=self.xbound
                self.pos[1]-=self.ybound/2
class player():
    def __init__(self):
        self.direction = [0,0]
        self.pos = [width/2,height/2]
        self.speed = 5
        self.tears=[]
        self.hp=60
        self.maxteartimer=10
        self.teartimer=0
        self.ybound=100
        self.xbound=100
        self.invincibility_timer=0
        self.maxinvincibility_timer=21
        self.damage = 1
        self.coins=0
        self.Giovaimg = ImageTk.PhotoImage(Image.open("Isaac.png").resize((self.xbound,self.ybound)))
        self.init_draw()
    def init_draw(self):
        self.player_geometry = tk.Canvas(height=self.ybound,width=self.xbound)
        self.player_geometry.create_image(self.xbound/2,self.ybound/2,image=self.Giovaimg)
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
        
        
        for enemy in world.currentroom.enemies:
            if detect_collision(self,enemy):
                self.take_damage(1)
                return 2
        for object in world.currentroom.environment:
            if detect_collision(self,object):
                return 2
        for tear in world.currentroom.enemy_tears:
            if detect_collision(tear,self):
                self.take_damage(1)
                tear.die()
                return 1
        for powerup in world.currentroom.power_up:
            if detect_collision(powerup,self):
                powerup.generate_powerup()
                return 3
        for coin in world.currentroom.coins:
            if detect_collision(coin,self):
                self.coins+=1

                print(self.coins)
                return 3
        return 0
    def take_damage(self,damage):
        if self.invincibility_timer==0:
            if self.hp==0:
                sys.exit()
            else:
                self.hp-=damage
                self.invincibility_timer=1
    def Door_Move(self,direction):
        margin=50
        doorxbound=100
        doorybound=20
        match direction:
            case 0:
                self.pos[0]=width/2-doorxbound/2
                self.pos[1]=margin
            case 1:
                self.pos[0]=margin
                self.pos[1]=(height-self.ybound)/2
            case 2:
                self.pos[1]=height-self.ybound-margin
                self.pos[0]=(width-doorxbound)/2
            case 3:
                self.pos[0]=width-self.xbound-margin
                self.pos[1]=(height-self.ybound)/2
class Tear():
    def __init__(self):
        self.direction=[0,0]
        self.pos=Giova.pos.copy()
        self.speed=10
        self.timer=100
        self.xbound=10
        self.ybound=10
        self.momentum=[Giova.direction[0]*1.5,Giova.direction[1]*1.5]
        self.init_draw()

    def init_draw(self):
        self.tear_geometry = tk.Canvas(window,bg="green",height=self.ybound,width=self.xbound)
        
    def update_state(self):
        self.timer-=1
        if self.timer<=0:
            self.die()
        else:
            self.pos = [self.pos[0]+self.direction[0]*self.speed+self.momentum[0],self.pos[1]+self.direction[1]*self.speed+self.momentum[1]]
            self.tear_geometry.place(x=self.pos[0],y=self.pos[1])
            for obj in world.currentroom.environment:
                if detect_collision(self,obj) and self in Giova.tears:
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
        self.speed=5
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
            for obj in world.currentroom.environment:
                if detect_collision(self,obj) and self in world.currentroom.enemy_tears:
                    self.die()
    def die(self):
        
            world.currentroom.enemy_tears.remove(self)
            self.tear_geometry.place_forget()
            self.tear_geometry.delete()
            self.tear_geometry.destroy()




class Static_Enemy():
    def __init__(self):
        self.direction=[0,0]
        self.pos=[700,350]
        self.ybound=100
        self.xbound=100
        self.timer=100
        self.timerdefault=100
        self.hp=4
        self.enemy_geometry = tk.Canvas(window,bg="red",height=self.ybound,width=self.xbound)
        
    def update_state(self):
        self.enemy_geometry.place(x=self.pos[0],y=self.pos[1])
        if self.hp<=0:
            kill_enemy(self)
        else:
            self.detect_collisions()
            self.timer-=1
            if self.timer==0:
                dir = [Giova.pos[0]-self.pos[0],Giova.pos[1]-self.pos[1]]
                newtear=Enemy_Tear()
                newtear.pos=[self.pos[0]+self.xbound/2,self.pos[1]+self.ybound/2]
                newtear.direction = normalize_vector(dir)
                world.currentroom.enemy_tears.append(newtear)
                
                
                self.timer=self.timerdefault
        
    def detect_collisions(self):
        for tear in Giova.tears:

            if detect_collision(tear,self):
                self.hp-=Giova.damage
                tear.die()
                break
    def die(self):
class Follow_Enemy():
    def __init__(self):
        self.direction=[0,0]
        self.speed = 2
        self.pos=[500,700]
        self.ybound=200
        self.xbound=200
        self.timer=100
        self.timerdefault=100
        self.hp=10
        self.enemy_geometry = tk.Canvas(window,bg="red",height=self.ybound,width=self.xbound)
    def update_state(self):
        if self.hp<=0:
            kill_enemy(self)
        else:
            oldpos=self.pos.copy()
            dir = [Giova.pos[0]-self.pos[0],Giova.pos[1]-self.pos[1]]
            self.direction=normalize_vector(dir)
            self.pos= [self.pos[0]+self.direction[0]*self.speed,self.pos[1]+self.direction[1]*self.speed]
            self.enemy_geometry.place(x=self.pos[0],y=self.pos[1])
            if enemy_collisions(self)==2:
                self.pos=oldpos
                    
    def die(self):

class Random_Enemy():
    def __init__(self):
        self.direction=[0,0]
        self.speed = 6
        self.pos=[800,700]
        self.ybound=100
        self.xbound=100
        self.timer=20
        self.timerdefault=20
        self.hp=10
        self.random=[1,1]

        self.enemy_geometry = tk.Canvas(window,bg="red",height=self.ybound,width=self.xbound)

    def update_state(self):
        if self.hp<=0:
            kill_enemy(self)
        else:
            self.timer-=1
            if self.timer<=0:
                self.timer=self.timerdefault
                self.random=random.choices(random_dir, weights=[3,2,7,8,7],k=2)
            oldpos=self.pos.copy()
            dir = [Giova.pos[0]-self.pos[0],Giova.pos[1]-self.pos[1]]
            self.direction=normalize_vector(dir)
            self.pos= [self.pos[0]+self.direction[0]*self.speed*self.random[0],self.pos[1]+self.direction[1]*self.speed*self.random[0]]
            self.enemy_geometry.place(x=self.pos[0],y=self.pos[1])
            if enemy_collisions(self)==2:
                self.pos=oldpos

class Wall():
    def __init__(self):
        self.pos=[500,500]
        self.ybound=100
        self.xbound=100
        self.enemy_geometry = tk.Canvas(window,bg="black",height=100,width=100)
    def update(self):
        self.enemy_geometry.place(x=self.pos[0],y=self.pos[1])
    def die(self):
        self.enemy_geometry.place_forget()
        self.enemy_geometry.delete()
        #self.enemy_geometry.destroy()
        world.currentroom.environment.remove(self)
        

class Coin():
    def __init__(self):
            self.pos=[900,500]
            self.ybound=25
            self.xbound=25
            self.geometry = tk.Canvas(window,bg="yellow",height=self.xbound,width=self.ybound)
    def update(self):
            world.currentroom.coins.append(self)
            self.geometry.place(x=self.pos[0],y=self.pos[1])
    def die(self):
        self.geometry.place_forget()
        self.geometry.delete()
        world.currentroom.coins.remove(self)
            



def input(event):
    pressed=event.keycode
    if pressed in orientations:
        rotate=orientations[pressed]
        Giova.direction[rotate[0]]=rotate[1]
        #print(f"updating state keycode:{pressed}, rotation {Giova.direction}")   
       
    elif pressed in arrows and Giova.teartimer==Giova.maxteartimer:
        Giova.teartimer=0
        new_tear=Tear()
        spawn_tear(pressed,new_tear,Giova)
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
    for enemy in world.currentroom.enemies:
        enemy.update_state()
    if not world.currentroom.enemies:
        world.currentroom.cleared=True
    for enemy_tear in world.currentroom.enemy_tears:
        enemy_tear.update_state()
    for door in world.currentroom.door_objects:
        door.detect_collision()
    window.after(20,update)


Giova = player()
"""enemies=[]
enemy_tears=[]
environment=[]"""


"""Level generation stuff"""
class PowerUp():
    def __init__(self) -> None:
        self.pos = [0,0]
        self.xbound= 100
        self.ybound=100
        self.index=random.randint(0,2)
    def draw(self):
        self.powerup_geometry= tk.Canvas(window,bg="purple",height=self.ybound,width=self.xbound)
        self.powerup_geometry.place(x=self.pos[0],y=self.pos[1])

    def generate_powerup(self):
        world.currentroom.cleared=True
        
        match self.index:
            case 0:
                Giova.damage+=random.randint(1,4)
                print(f"Damage:{Giova.damage}")
            case 1:
                Giova.hp += 2
                print(f"HP:{Giova.hp}")
            case 2:
                Giova.speed+=random.randint(1,3)
                print(f"Speed:{Giova.speed}")
        self.die()

    def die(self):
        world.currentroom.power_up.remove(self)
        self.powerup_geometry.place_forget()
        self.powerup_geometry.delete()
        self.powerup_geometry.destroy()

    
"""
This generates a phantom block
"""
environment_options=[[Wall()],[]]

                            newroom_coordinates=(room_coordinates[0]+directions[door_direction][0],room_coordinates[1]+directions[door_direction][1])




class Room():
    def __init__(self):
        self.doors=[None]*4
        self.door_objects=[]
        self.enemies=[]
        self.power_up=[]
        self.environment=[]
        self.enemy_tears=[]
        self.coins=[]
        self.cleared=False
        self.coordinates=[0,0]
        self.type="normal"
        self.env_type=random.choice(environment_options)
        print(self.env_type)

    def generate_position(self, enemy):
        """
        This should be rewritten
        """
        enemy.pos= [random.randint(150,1800), random.randint(150,950)]
        objectt=0
        
        for objectt in (self.environment):
            if detect_collision(enemy,objectt):
                self.generate_position(enemy)
                return      
        for objectt in self.enemies:
            if detect_collision(enemy,objectt):
                self.generate_position(enemy)
                return 

    def generate(self,world):
        #Spawning doors
        self.environment=self.env_type.copy()
        
        print(self.environment,self.env_type)
        for obj in self.environment:
            obj.update()
        for i in range(4):
            if self.doors[i]==1:
                door=Door()
                door.pos=door_positions[i].copy()            
                rotate(door,i)
                door.direction=i
                match world.rooms[(self.coordinates[0]+directions[i][0],self.coordinates[1]+directions[i][1])].type:
                    case "boss":
                        door.color="purple"
                    case "shop":
                        door.color="orange"
                    case "treasure":
                        door.color="yellow"
                door.spawn()
                
                self.door_objects.append(door)
            
            
        match self.type:
            case "normal":
                #Might be added to other type of room
                if not self.cleared:
                    enemy_number=random.randint(2,5)
                    for i in range(enemy_number):
                        enemy_type=random.randint(0,2)
                        match enemy_type:
                            case 0:
                                enemy=Static_Enemy()
                            case 1:
                                enemy=Follow_Enemy()
                            case 2:
                                enemy=Random_Enemy()
                        self.generate_position(enemy)
                        self.enemies.append(enemy)

                    
            case "shop":
                ...
            case "boss":
                ...
            case "treasure":
                if not self.cleared:
                    powNum= random.randint(1,2)
                    for i in range(powNum):
                        powerup = PowerUp()
                        self.generate_position(powerup)
                        powerup.draw()
                        self.power_up.append(powerup)
                        print("spawned")
            
    

class Door():
    def __init__(self) -> None:
        self.xbound=100
        self.ybound=20
        self.pos=[0,0]
        self.direction=0
        self.color="brown"
    def spawn(self):
        self.door_geometry = tk.Canvas(window,bg=self.color,height=self.ybound,width=self.xbound)
        self.door_geometry.place(x=self.pos[0],y=self.pos[1])
    
    def detect_collision(self):
        
        if world.currentroom.cleared ==True and detect_collision(Giova,self):
            print("AAAAAAAAA")
            
            world.newroom(self.direction)
            
    def die(self):
        world.currentroom.door_objects.remove(self)
        self.door_geometry.place_forget()
        self.door_geometry.delete()
        self.door_geometry.destroy()



class World():
    def __init__(self):
        self.max_rooms=random.randint(6,11)
        self.generated_rooms=1
        self.current_boss_rooms=0
        self.current_treasure_rooms=0
        self.current_shop_rooms=0
        self.rooms={(0,0):Room()}
        self.frontier=[(0,0)]
        self.currentroom=self.rooms[(0,0)]
        while self.generated_rooms<self.max_rooms:
            if self.frontier:
                room_coordinates=self.frontier[-1]
                self.frontier.pop()
                current_room=self.rooms[room_coordinates]
                #The directions are: TOP,LEFT,BOTTOM,RIGHT
                for door_direction in range(4):
                    #creates doors in the current room
                    door_chance=random.randint(0,1)
                    if current_room.doors[door_direction]==None:
                        current_room.doors[door_direction]=door_chance
                        if door_chance==1:
                            
                            newroom_coordinates=(room_coordinates[0]+directions[door_direction][0],room_coordinates[1]+directions[door_direction][1])
                            if newroom_coordinates not in self.rooms:
                                #generate a room
                                self.generated_rooms+=1
                                if self.current_boss_rooms==0:
                                    boss_chance=random.randint(self.generated_rooms,20)
                                if self.current_treasure_rooms<=1:
                                    treasure_chance=random.randint(0,4)
                                if self.current_shop_rooms==0:
                                    shop_chance=random.randint(0,4)
                                
                                #this is to ensure we get a boss room
                                newroom=Room()
                                self.rooms[newroom_coordinates]=newroom
                                if boss_chance>=17 or (self.max_rooms-self.generated_rooms<=2 and self.current_boss_rooms==0):
                                    self.current_boss_rooms+=1
                                    newroom.type="boss"

                                    boss_chance=0
                                elif treasure_chance==4:
                                    self.current_treasure_rooms+=1
                                    newroom.type="treasure"
                                    treasure_chance=0
                                elif shop_chance==4:
                                    self.current_shop_rooms+=1
                                    newroom.type="shop"
                                    shop_chance=0
                                else:
                                    newroom.type="normal"
                                self.frontier.append(newroom_coordinates)
                            self.rooms[newroom_coordinates].doors[(door_direction+2)%4]=1
                            newroom.coordinates=newroom_coordinates
        self.currentroom.type="start"
        self.currentroom.generate(self)
    def newroom(self,direction):
        while self.currentroom.enemies:
            self.currentroom.enemies[0].die()
        while self.currentroom.enemy_tears:
            self.currentroom.enemy_tears[0].die()
        while self.currentroom.environment:
            self.currentroom.environment[0].die()
        while self.currentroom.door_objects:
            self.currentroom.door_objects[0].die()
        while Giova.tears:
            Giova.tears[0].die()
        while self.currentroom.power_up:
            self.currentroom.power_up[0].die()
        self.currentroom=self.rooms[self.currentroom.coordinates[0]+directions[direction][0],self.currentroom.coordinates[1]+directions[direction][1]]
        direction=(direction+2)%4
        Giova.Door_Move(direction)
        self.currentroom.generate(self)
world=World()      
        
        



update()
window.bind("<KeyPress>",input)
window.bind("<KeyRelease>",release)
window.mainloop()