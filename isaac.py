#TODO Fix Input(you cant move and shoot at the same time)
# Random enemy collisions are broken
#Fix coin pickups being doubled
#Gli sfondi non sono allineati
import tkinter as tk
import tkinter.font as font
import math
import random
import sys
from PIL import ImageTk, Image
from tkinter import messagebox
import copy
sys.setrecursionlimit(9999)
room_xbound=130
room_ybound=140

random_dir=[-1,-0.5,0,1,0.5]
window = tk.Tk()
window.attributes("-fullscreen",False)
window.iconphoto(True,ImageTk.PhotoImage(Image.open("Isaac.png")))
window.title("The Binding of Giovanni")
width=1920
height=1080
bg = tk.Canvas(window,width=1920,height=1080,background="black")

"""
IMAGES
"""
roomsimgs=[ImageTk.PhotoImage(Image.open("room0.png").resize((1920,1080))), 
           ImageTk.PhotoImage(Image.open("room1.png").resize((1920,1080)))]

special_roomsimgs=[ImageTk.PhotoImage(Image.open("shoproom.png").resize((1920,1080))),  #shop
           ImageTk.PhotoImage(Image.open("bossroom.png").resize((1920,1080))), #boss
           ImageTk.PhotoImage(Image.open("itemroom.png").resize((1920,1080))), #treasure
           ImageTk.PhotoImage(Image.open("startroom.png").resize((1920,1080))) #start
           ]


powerupimgs=[
    ImageTk.PhotoImage(Image.open("shotgun.png").resize((100,100))), #Damage
    ImageTk.PhotoImage(Image.open("hpup.png").resize((100,100))), #Hp
    ImageTk.PhotoImage(Image.open("shoe.png").resize((100,100))) #Speed
]
coinimg= ImageTk.PhotoImage(Image.open("coin.png").resize((25,25)))
heartimg=ImageTk.PhotoImage(Image.open("heart.png").resize((50,50)))


head_img=ImageTk.PhotoImage(Image.open("coin.png").resize((400,400)))
hand_img=ImageTk.PhotoImage(Image.open("coin.png").resize((250,250)))

followenemy_img = ImageTk.PhotoImage(Image.open("BigBro.png").resize((150,150)))
randomenemy_img = ImageTk.PhotoImage(Image.open("BigBro.png").resize((150,150)))

sfondo = bg.create_image(width/2,height/2,image=roomsimgs[0])
window.wm_attributes('-transparentcolor','#add123')
window.geometry("1920x1080")



ismenu =True

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
shooting = False
#directions=[(0,1),(1,0),(0,-1),(-1,0)]
directions=[(0,-1),(-1,0),(0,1),(1,0)]

door_positions=([width/2,room_ybound],[room_xbound-4.9,height/2],[width/2,height-room_ybound+15],[width-room_xbound-10.5,height/2])
powerup_positions=[[360,500],[960,500],[1560,500]]

fonT = font.Font(size=50,family="hooge 05_55")
titleFont= font.Font(size=100,weight="bold",family="hooge 05_55")
smallfont = font.Font(size=35,family="hooge 05_55")

def kill_enemy(object):
    chance=random.randint(1,10)
    if chance<=5:
        coin=Coin()
        coin.pos=[object.pos[0]+object.xbound/2,object.pos[1]+object.ybound/2]
        coin.update()
    elif chance==10:
        print("sium")
        heart=Heart()
        heart.pos=[object.pos[0]+object.xbound/2,object.pos[1]+object.ybound/2]
        heart.update()
    world.currentroom.enemies.remove(object)
    bg.delete(object.enemy_geometry)

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
class Menu():
    def __init__(self) -> None:
        self.font = font.Font(size=50,family="hooge 05_55")
        self.titleFont= font.Font(size=100,weight="bold",family="hooge 05_55")
        self.menubg=tk.Canvas(width=width,height=height,bg="Black")
        self.sfondo = self.menubg.create_image(width/2,height/2,image=roomsimgs[0])
        self.title=self.menubg.create_text(width/2,300,text="The Binding Of Giova",font=titleFont,fill="#FEFAE0")
        
        
        self.playbtn = tk.Button(window,text="Start",command=self.play,relief="ridge",width=50,height=2,font=fonT,bg="#386641",activebackground="#6a994e",fg="#FEFAE0")
        self.quitbtn = tk.Button(window,text="Quit",command=sys.exit,relief="ridge",font=fonT,bg="#386641",activebackground="#6a994e",fg="#FEFAE0")
        self.xbound =800
        self.ybound=100
        self.place()
        
    def place(self):
        self.menubg.place(x=0, y= 0)
        self.playbtn.place(x=width/2-self.xbound/2,y=500,width=self.xbound,height=self.ybound)
        self.quitbtn.place(x=width/2-self.xbound/2,y=650,width=self.xbound,height=self.ybound)
        
        
    
    def play(self):
        global ismenu
        ismenu = False
        
        self.die()
        pass
    
    def die(self):
        self.menubg.destroy()
        self.playbtn.destroy()
        self.quitbtn.destroy()



        
class player():
    def __init__(self):
        self.direction = [0,0]
        self.lastdir= [0,0]
        self.pos = [width/2,height/2]
        self.speed = 15 #og is 5
        self.tears=[]
        self.hp=3
        self.hearts=[]
        self.max_hp=6
        self.maxteartimer=10
        self.teartimer=0
        self.ybound=100
        self.xbound=100
        self.invincibility_timer=0
        self.maxinvincibility_timer=10
        self.damage = 100
        self.coins=0
        self.coinslabel = bg.create_text(1800,60,text=f"x{self.coins}",font=smallfont,fill="#FEFAE0")
        self.coinicon=bg.create_image(1730,50,image=coinimg,anchor='nw')
        self.Giovaimg = ImageTk.PhotoImage(Image.open("front.png").resize((self.xbound,self.ybound)))
        self.player_geometry = bg.create_image(self.pos[0],self.pos[1],image=self.Giovaimg,anchor='nw') 
        self.draw_hearts()
        self.init_draw()
        
    def init_draw(self):
        bg.delete(self.player_geometry)
        self.player_geometry = bg.create_image(self.pos[0],self.pos[1],image=self.Giovaimg,anchor='nw')
    def update_state(self):
        
        #If going diagonally
        oldpos=self.pos.copy()
        self.lastdir=self.direction.copy()
        if self.direction[0]&self.direction[1]:
            self.pos = [self.pos[0]+self.direction[0]*self.speed*math.sqrt(2)/2,self.pos[1]+self.direction[1]*self.speed*math.sqrt(2)/2]
        else:
            self.pos = [self.pos[0]+self.direction[0]*self.speed,self.pos[1]+self.direction[1]*self.speed]
        #self.player_geometry.place(x=self.pos[0],y=self.pos[1])
        delta=[self.pos[0]-oldpos[0],self.pos[1]-oldpos[1]]
        if delta[0]!=0 or delta[1]!=0:
            #bg.move(self.player_geometry,delta[0],delta[1])
            bg.moveto(self.player_geometry,self.pos[0],self.pos[1])
        if self.teartimer<self.maxteartimer:
            self.teartimer+=1
        if self.detect_collisions()==2 or(self.pos[0]<room_xbound) or(self.pos[1]<room_ybound) or (self.pos[0]+self.xbound>width-room_xbound) or (self.pos[1]+self.ybound>height-room_ybound+12):
            self.pos=oldpos

        """
        THIS COULD PROBABLY BE DONE IN A CLEANER WAY
        """
        if self.invincibility_timer==self.maxinvincibility_timer-1:
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

                coin.die()
                self.coins+=1
                self.updateCoins()
                #print(self.coins)
                return 3
        for heart in world.currentroom.hearts:
            if detect_collision(heart,self):
                
                if self.hp<self.max_hp:
                    heart.die()
                    self.hp+=1
                    self.draw_hearts()
                return 3
        if world.currentroom.type=="boss":
            boss=world.currentroom.boss
            if detect_collision(self,boss.left_hand) or detect_collision(self,boss.right_hand):
                self.take_damage(1)

                return 2
        return 0
    def take_damage(self,damage):
        if self.invincibility_timer==0:
            if self.hp==0:
                messagebox.showinfo("The Binding of Giova","Sei Morto")
                sys.exit()
            else:
                self.hp-=damage
                self.invincibility_timer=1
                bg.delete(self.hearts[-1])
                self.hearts.pop()
                print(self.hearts)
    def Door_Move(self,direction):
        margin=50
        doorxbound=100
        doorybound=20
        match direction:
            case 0:
                self.pos[0]=width/2-doorxbound/2
                self.pos[1]=margin+room_xbound
            case 1:
                self.pos[0]=margin+room_ybound
                self.pos[1]=(height-self.ybound)/2
            case 2:
                self.pos[1]=height-self.ybound-margin-room_ybound
                self.pos[0]=(width-doorxbound)/2
            case 3:
                self.pos[0]=width-self.xbound-margin-room_xbound
                self.pos[1]=(height-self.ybound)/2
    
    def draw_hearts(self):
        self.posx=50
        for i in self.hearts:
            bg.delete(i)
        self.hearts=[]
        for i in range(self.hp):
            heart = bg.create_image(self.posx,50,image=heartimg,anchor='nw')
            self.hearts.append(heart)
            self.posx+=50
    def updateCoins(self):
        bg.delete(self.coinslabel)
        self.coinslabel = bg.create_text(1800,60,text=f"x{self.coins}",font=smallfont,fill="#FEFAE0")

            


        
    

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
        self.tear_geometry = tk.Canvas(window,bg="cyan",height=self.ybound,width=self.xbound)
    def update_state(self):
        self.timer-=1
        if self.timer<=0:
            self.die()
        else:
            self.pos = [self.pos[0]+self.direction[0]*self.speed+self.momentum[0],self.pos[1]+self.direction[1]*self.speed+self.momentum[1]]
            self.tear_geometry.place(x=self.pos[0],y=self.pos[1])
            if (self.pos[0]<room_xbound) or(self.pos[1]<room_ybound) or (self.pos[0]+self.xbound>width-room_xbound) or (self.pos[1]+self.ybound>height-room_ybound+12):
                self.die()
            for obj in world.currentroom.environment:
                if detect_collision(self,obj)and self in Giova.tears:
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
        self.timer=random.randint(1,99)
        self.timerdefault=random.randint(80,120)
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
class Follow_Enemy():
    def __init__(self):
        self.direction=[0,0]
        self.speed = 2
        self.pos=[500,700]
        self.ybound=100
        self.xbound=100
        self.timer=100
        self.timerdefault=100
        self.hp=10
        self.enemy_geometry = bg.create_image(self.pos[0],self.pos[1],image=followenemy_img,anchor='nw')


    def update_state(self):
        if self.hp<=0:
            kill_enemy(self)
        else:
            oldpos=self.pos.copy()
            dir = [Giova.pos[0]-self.pos[0],Giova.pos[1]-self.pos[1]]
            self.direction=normalize_vector(dir)
            self.pos= [self.pos[0]+self.direction[0]*self.speed,self.pos[1]+self.direction[1]*self.speed]
            delta=[self.pos[0]-oldpos[0],self.pos[1]-oldpos[1]]
            if delta[0]!=0 or delta[1]!=0:
            #bg.move(self.player_geometry,delta[0],delta[1])
                bg.moveto(self.enemy_geometry,self.pos[0],self.pos[1])
            if enemy_collisions(self)==2:
                self.pos=oldpos

class Random_Enemy():
    def __init__(self):
        self.direction=[0,0]
        self.speed = 6
        self.pos=[800,700]
        self.ybound=100
        self.xbound=100
        self.timer=random.randint(0,19)
        self.timerdefault=20
        self.hp=10
        self.random=[1,1]

        self.enemy_geometry = bg.create_image(self.pos[0],self.pos[1],image=randomenemy_img,anchor='nw')

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
            delta=[self.pos[0]-oldpos[0],self.pos[1]-oldpos[1]]
            if delta[0]!=0 or delta[1]!=0:
            #bg.move(self.player_geometry,delta[0],delta[1])
                bg.moveto(self.enemy_geometry,self.pos[0],self.pos[1])
            #we can remove the boundary checks for more performance but possibly out of bounds enemies
            if enemy_collisions(self)==2 or(self.pos[0]<room_xbound) or(self.pos[1]<room_ybound) or (self.pos[0]+self.xbound>width-room_xbound) or (self.pos[1]+self.ybound>height-room_ybound+12):
                self.pos=oldpos

#This is horribly written
class Boss_main():
    
    def __init__(self):
        print("spawning boss")
        self.hp=60
        self.timer=200
        self.timer_max=200 #the normal val is 200
        self.action=0
        
    def spawn(self):
        self.head=Boss_head()
        self.left_hand=Boss_hand()
        self.right_hand=Boss_hand()
        self.right_hand.pos=[1260,150]
        self.right_hand.speed=20
        self.left_hand.spawn()
        self.right_hand.spawn()
    def update_state(self):
        self.timer-=1
        if self.timer==0:
            self.timer=self.timer_max
            self.action=random.randint(1,5)
        match self.action:
            case 1:
                if self.timer %50==0:
                    tear_number=random.randint(8,14)
                    for i in range(tear_number):
                        enemy_tear=Enemy_Tear()
                        enemy_tear.pos=[width/tear_number*i,500]
                        enemy_tear.direction=[0,1]
                        world.currentroom.enemy_tears.append(enemy_tear)
            case 2: #left hand
                print("left hand")
                if self.timer>=80 and self.left_hand.pos[1]<580:
                    self.left_hand.pos[1]+=self.left_hand.speed
                elif self.timer>=80 and self.left_hand.pos[0]<1500:
                    self.left_hand.pos[0]+=self.left_hand.speed
                elif self.timer<=80 and self.left_hand.pos[0]>385:
                    self.left_hand.pos[0]-=self.left_hand.speed
                elif self.timer<=80 and self.left_hand.pos[1]>150:
                    self.left_hand.pos[1]-=self.left_hand.speed
                self.left_hand.update()
                
            case 3: #right hand
                print("right hand")
                if self.timer>=80 and self.right_hand.pos[1]<580:
                    self.right_hand.pos[1]+=self.right_hand.speed
                elif self.timer>=80 and self.right_hand.pos[0]>150:
                    self.right_hand.pos[0]-=self.right_hand.speed
                elif self.timer<=80 and self.right_hand.pos[0]<1260:
                    self.right_hand.pos[0]+=self.right_hand.speed
                elif self.timer<=80 and self.right_hand.pos[1]>150:
                    self.right_hand.pos[1]-=self.right_hand.speed
                self.right_hand.update()
            case 4: #front
                if self.timer %50==0:
                    for i in range(7):
                        enemy_tear=Enemy_Tear()
                        enemy_tear.speed*=2
                        enemy_tear.pos=[760+66*i,500]
                        enemy_tear.direction=[0,1]
                        world.currentroom.enemy_tears.append(enemy_tear)
            case 5:
                if self.timer%50==0 or self.timer==0:
                    enemy_tear=Enemy_Tear()
                    enemy_tear.timer=500
                    enemy_tear.speed*=2
                    enemy_tear.pos=[100,900]
                    enemy_tear.direction=[1,0]
                    world.currentroom.enemy_tears.append(enemy_tear)
        #checks collisions
        for tear in Giova.tears:
            if detect_collision(tear,self.head) or detect_collision(tear,self.right_hand) or detect_collision(tear,self.left_hand):
                print("head",tear.pos,self.head.pos)
                self.hp-=Giova.damage
                print(self.hp)
                tear.die()
        if self.hp<=0:
            self.die()
    def die(self):
        messagebox.showinfo("The Binding of  Giova","Hai Vinto")
        sys.exit()
class Boss_head():
    def __init__(self):
       self.xbound=400
       self.ybound=400
       self.pos=[760,150]
       #self.enemy_geometry = tk.Canvas(window,bg="red",height=self.ybound,width=self.xbound)
       #self.enemy_geometry.place(x=self.pos[0],y=self.pos[1])
       self.head_id=bg.create_image(self.pos[0],self.pos[1],image=head_img,anchor='nw')
    

class Boss_hand():
    def __init__(self):
        self.xbound=250
        self.ybound=250
        self.pos=[385,150]
        self.speed=20
    def spawn(self):
        self.hand_id=bg.create_image(self.pos[0],self.pos[1],image=hand_img,anchor='nw')
        #self.enemy_geometry = tk.Canvas(window,bg="red",height=self.ybound,width=self.xbound)
        #self.enemy_geometry.place(x=self.pos[0],y=self.pos[1])
    def update(self):
        bg.moveto(self.hand_id,self.pos[0],self.pos[1])
        #self.enemy_geometry.place(x=self.pos[0],y=self.pos[1])

class Wall():
    def __init__(self):
        self.pos=[300,500]
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
    def update(self):
            world.currentroom.coins.append(self)
            self.geometry = bg.create_image(self.pos[0],self.pos[1],image=coinimg,anchor='nw') 
    def die(self):
        bg.delete(self.geometry)
        world.currentroom.coins.remove(self)
            
class Heart():
    def __init__(self):
            self.pos=[900,500]
            self.ybound=25
            self.xbound=25
    def update(self):
            world.currentroom.hearts.append(self)
            self.geometry = bg.create_image(self.pos[0],self.pos[1],image=heartimg,anchor='nw') 
    def die(self):
        bg.delete(self.geometry)
        world.currentroom.hearts.remove(self)
            


def input(event):
    pressed=event.keycode
    if pressed in orientations:
        rotate=orientations[pressed]
        Giova.direction[rotate[0]]=rotate[1]        
            #print(f"updating state keycode:{pressed}, rotation {Giova.direction}")
        if not shooting and Giova.lastdir!=Giova.direction:
            if Giova.direction[1] == -1 :
                Giova.Giovaimg = ImageTk.PhotoImage(Image.open("back.png").resize((Giova.xbound,Giova.ybound)))
            elif Giova.direction[1] == 1:
                Giova.Giovaimg = ImageTk.PhotoImage(Image.open("front.png").resize((Giova.xbound,Giova.ybound)))
            else:
                if Giova.direction[0] == 1:
                    Giova.Giovaimg = ImageTk.PhotoImage(Image.open("destra.png").resize((Giova.xbound,Giova.ybound)))
                elif Giova.direction[0] == -1:
                    Giova.Giovaimg = ImageTk.PhotoImage(Image.open("sinistra.png").resize((Giova.xbound,Giova.ybound)))
                    

                      
    elif pressed in arrows and Giova.teartimer==Giova.maxteartimer:
        Giova.teartimer=0
        new_tear=Tear()
        spawn_tear(pressed,new_tear,Giova)
        Giova.tears.append(new_tear)
        match pressed:
            case 37:
                Giova.Giovaimg = ImageTk.PhotoImage(Image.open("sinistra.png").resize((Giova.xbound,Giova.ybound)))
            case 38:
                Giova.Giovaimg = ImageTk.PhotoImage(Image.open("back.png").resize((Giova.xbound,Giova.ybound)))
            case 39:
                Giova.Giovaimg = ImageTk.PhotoImage(Image.open("destra.png").resize((Giova.xbound,Giova.ybound)))
            case 40:
                Giova.Giovaimg = ImageTk.PhotoImage(Image.open("front.png").resize((Giova.xbound,Giova.ybound)))
    
    Giova.init_draw()
def release(event):
    global shooting
    pressed=event.keycode
    if pressed in orientations:
        rotate=orientations[pressed]
        Giova.direction[rotate[0]]=0
        #print(f"Deleting state keycode:{pressed}, rotation {Giova.direction}")
    if pressed in arrows:
        shooting = False

def update():
    print(world.currentroom.coordinates)
    if not ismenu:
        Giova.update_state()
        for single_tear in Giova.tears:
            single_tear.update_state()
        for enemy in world.currentroom.enemies:
            enemy.update_state()
        
        for enemy_tear in world.currentroom.enemy_tears:
            enemy_tear.update_state()
        for door in world.currentroom.door_objects:
            door.detect_collision()
        if world.currentroom.boss:
            world.currentroom.boss.update_state()
        elif not world.currentroom.enemies:
            world.currentroom.cleared=True
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
        self.text=0
        self.price=0
        
    def draw(self):
        self.geometry = bg.create_image(self.pos[0],self.pos[1],image=powerupimgs[self.index],anchor='nw') 
        #self.powerup_geometry= tk.Canvas(window,bg="purple",height=self.ybound,width=self.xbound)
        #self.powerup_geometry.place(x=self.pos[0],y=self.pos[1])
        if self.price>0:
            self.text=bg.create_text(self.pos[0]+self.xbound/2,self.pos[1]-30,text=self.price,font=smallfont,fill="#FEFAE0")
            

    def generate_powerup(self):
        world.currentroom.cleared=True
        if Giova.coins>=self.price:
            Giova.coins-=self.price
            Giova.updateCoins()
            match self.index:
                case 0:
                    Giova.damage+=random.randint(1,4)
                    print(f"Damage:{Giova.damage}")
                case 1:
                    Giova.hp=Giova.max_hp
                    Giova.max_hp+=1
                    Giova.draw_hearts()
                    print(f"HP:{Giova.hp}")
                case 2:
                    Giova.speed+=random.randint(1,3)
                    print(f"Speed:{Giova.speed}")
            self.die()

    def die(self):
        bg.delete(self.geometry)
        world.currentroom.power_up.remove(self)
        if self.price>0:
            bg.delete(self.text)
        """self.powerup_geometry.place_forget()
        self.powerup_geometry.delete()
        self.powerup_geometry.destroy()"""
        


"""

Envrironment stuff
"""
environment_options=[[Wall()],[]]
walls=[]
for i in range(3):
    wall=Wall()
    wall.pos[0]=500+500*i
    walls.append(wall)
environment_options.append(walls)
walls=[]
for i in range(3):
    wall=Wall()
    wall.pos=[width/2-150+100*i,height/2-50]
    walls.append(wall)
environment_options.append(walls)
walls=[]





class Room():
    def __init__(self):
        self.doors=[None]*4
        self.door_objects=[]
        self.enemies=[]
        self.power_up=[]
        self.environment=[]
        self.enemy_tears=[]
        self.coins=[]
        self.hearts=[]
        self.cleared=False
        self.coordinates=(0,0)
        self.type="normal"
        self.env_type=random.choice(environment_options)
        self.roomimg = roomsimgs[random.randint(0,1)]
        self.boss=None
        bg.place(y=0,x=0)
    def generate_position(self, enemy):
        """
        This should be rewritten
        """
        bound=300
        enemy.pos= [random.randint(room_xbound+bound,width-room_xbound-bound), random.randint(room_ybound+bound,height-room_ybound-bound)]
        objectt=0
        
        for objectt in (self.environment):
            if (enemy==Follow_Enemy and detect_collision(enemy,objectt)) or detect_collision(enemy,objectt):
                self.generate_position(enemy)
                return      
        for objectt in self.enemies:
            if (enemy==Follow_Enemy and detect_collision(objectt,enemy)) or detect_collision(enemy,objectt):
                self.generate_position(enemy)
                return 
            

    def generate(self,world):
        global sfondo
        bg.delete(sfondo)
        #Spawning doors
        
        
        for i in range(4):
            if self.doors[i]==1:
                door=Door()
                door.pos=door_positions[i].copy()            
                rotate(door,i)
                door.direction=i
                
                #this is to avoid crashes
                coordinates_holder=copy.deepcopy(self.coordinates)
                coordinates=(coordinates_holder[0]+directions[i][0],coordinates_holder[1]+directions[i][1])
                if coordinates in world.rooms:
                    match world.rooms[coordinates].type:
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
                sfondo = bg.create_image(width/2,height/2,image=self.roomimg)
                self.environment=self.env_type.copy()
        
                for obj in self.environment:
                    obj.update()
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
                
                sfondo = bg.create_image(width/2,height/2,image=special_roomsimgs[0])
                if not self.cleared:
                    for i in range(3):
                        price=random.randint(3,7)
                        powerup = PowerUp()
                        powerup.price=price
                        powerup.pos=powerup_positions[i]
                        powerup.draw()
                        self.power_up.append(powerup)
                        print("spawned")
                            
            case "boss":
                sfondo = bg.create_image(width/2,height/2,image=special_roomsimgs[1])
                self.cleared=False
                self.boss=Boss_main()
                self.boss.spawn()
                Giova.Door_Move(2)
                
                
            case "treasure":
                sfondo = bg.create_image(width/2,height/2,image=special_roomsimgs[2])
                if not self.cleared:
                    powNum= random.randint(1,2)
                    for i in range(powNum):
                        powerup = PowerUp()
                        powerup.pos=powerup_positions[i]
                        powerup.draw()
                        self.power_up.append(powerup)
                        print("spawned")
            case "start":
                sfondo = bg.create_image(width/2,height/2,image=special_roomsimgs[3])
        Giova.init_draw()
        for i in Giova.hearts:
            print("raised")
            bg.tag_raise(i)
        bg.tag_raise(Giova.coinicon)
        bg.tag_raise(Giova.coinslabel)
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
            #print("AAAAAAAAA")
            
            world.newroom(self.direction)
            
    def die(self):
        world.currentroom.door_objects.remove(self)
        self.door_geometry.place_forget()
        self.door_geometry.delete()
        self.door_geometry.destroy()



class World():
    def __init__(self):
        self.max_rooms=random.randint(10,15)
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
                    if not current_room.doors[door_direction]:
                        current_room.doors[door_direction]=door_chance
                        if door_chance==1:
                            
                            newroom_coordinates=(room_coordinates[0]+directions[door_direction][0],room_coordinates[1]+directions[door_direction][1])
                            if newroom_coordinates not in self.rooms:
                                #generate a room
                                self.generated_rooms+=1
                                if self.current_boss_rooms==0:
                                    boss_chance=random.randint(1,5)
                                if self.current_treasure_rooms<=2:
                                    treasure_chance=random.randint(0,4)
                                if self.current_shop_rooms==0:
                                    shop_chance=random.randint(0,5)
                                
                                #this is to ensure we get a boss room
                                newroom=Room()
                                self.rooms[newroom_coordinates]=newroom
                                if boss_chance+current_room.coordinates[0]+current_room.coordinates[1]>=10 or (self.max_rooms-self.generated_rooms<=2 and self.current_boss_rooms==0):
                                    print("boss at",newroom_coordinates)
                                    self.current_boss_rooms+=1
                                    newroom.type="boss"

                                    boss_chance=0
                                elif treasure_chance==4:
                                    print("treasure at",newroom_coordinates)
                                    self.current_treasure_rooms+=1
                                    newroom.type="treasure"
                                    treasure_chance=0
                                elif shop_chance+current_room.coordinates[0]+current_room.coordinates[1]>=4:
                                    print("shop at",newroom_coordinates)
                                    self.current_shop_rooms+=1
                                    newroom.type="shop"
                                    shop_chance=0
                                else:
                                    newroom.type="normal"
                                    self.frontier.append(newroom_coordinates)
                            self.rooms[newroom_coordinates].doors[(door_direction+2)%4]=1
                            newroom.coordinates=newroom_coordinates
            else:
                rooms=list(self.rooms.keys())
                choice=random.choice(rooms)
                if self.rooms[choice].type=="normal":
                    self.frontier.append(choice)
        self.currentroom.type="start"
        #self.currentroom.type="start"
        self.currentroom.generate(self)
        print(f"rooms: {self.generated_rooms} shops{self.current_shop_rooms} treasures {self.current_treasure_rooms}")
    def newroom(self,direction):
        #this is to avoid crashes
        print("direction",direction)
        coordinates_holder=copy.deepcopy(self.currentroom.coordinates)
        newroom_index=(coordinates_holder[0]+directions[direction][0],coordinates_holder[1]+directions[direction][1])
        if newroom_index in self.rooms:
            print("from",self.currentroom.coordinates)
            print("to",newroom_index)
            while self.currentroom.enemies:
                self.currentroom.enemies[0].die()
            while self.currentroom.enemy_tears:
                self.currentroom.enemy_tears[0].die()
            while self.currentroom.environment:
                self.currentroom.environment[0].die()
            while self.currentroom.door_objects:
                self.currentroom.door_objects[0].die()
            while self.currentroom.coins:
                self.currentroom.coins[0].die()
            while Giova.tears:
                Giova.tears[0].die()
            while self.currentroom.power_up:
                self.currentroom.power_up[0].die()
            while self.currentroom.hearts:
                self.currentroom.hearts[0].die()
            self.currentroom=self.rooms[newroom_index]
            #this is also to avoid weirdness
            self.currentroom.coordinates=newroom_index
            direction=(direction+2)%4
            Giova.Door_Move(direction)
            self.currentroom.generate(self)
            

world=World()      
Menuobj =Menu()

update()
window.bind("<KeyPress>",input)
window.bind("<KeyRelease>",release)
window.mainloop()