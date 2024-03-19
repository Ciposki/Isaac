
import tkinter as tk
import tkinter.font as font
import math
import random
import sys
from PIL import ImageTk, Image
from tkinter import messagebox
import copy
sys.setrecursionlimit(9999)
#dimensions to not make the player walk on walls
room_xbound=130
room_ybound=140

#multipliers for the random enemy's direction
random_dir=[-1,-0.5,0,1,0.5]
#Opens a tkinter window
window = tk.Tk()
window.attributes("-fullscreen",False)
#Adds an icon and a title
window.iconphoto(True,ImageTk.PhotoImage(Image.open("Isaac.png")))
window.title("The Binding of Giovanni")
#window dimensions
width=1920
height=1080
#creates a canvas.
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


head_img=ImageTk.PhotoImage(Image.open("netor1.png").resize((400,400)))
l_hand_img=ImageTk.PhotoImage(Image.open("lhand.png").resize((250,250)))
r_hand_img=ImageTk.PhotoImage(Image.open("rhand.png").resize((250,250)))

netor_scream_imgs=[
    ImageTk.PhotoImage(Image.open("netor1.png").resize((400,400))),
    ImageTk.PhotoImage(Image.open("netor2.png").resize((400,400))),
    ImageTk.PhotoImage(Image.open("netor3.png").resize((400,400))),
    ImageTk.PhotoImage(Image.open("netor4.png").resize((400,400)))
]
netor_chad_imgs=[
    ImageTk.PhotoImage(Image.open("netor1.png").resize((400,400))),
    ImageTk.PhotoImage(Image.open("netor5.png").resize((400,400))),
    ImageTk.PhotoImage(Image.open("netor6.png").resize((400,400))),
    ImageTk.PhotoImage(Image.open("netor7.png").resize((400,400)))
]

rockimg = ImageTk.PhotoImage(Image.open("Rock.png").resize((100,100)))
netor_scream_imgs+=netor_scream_imgs[::-1]
netor_chad_imgs+=netor_chad_imgs[::-1]
followenemy_img = ImageTk.PhotoImage(Image.open("bro.png").resize((100,100)))
randomenemy_img = ImageTk.PhotoImage(Image.open("gosts.png").resize((100,100)))
staticenemy_img = ImageTk.PhotoImage(Image.open("static.png").resize((100,100)))
sfondo = bg.create_image(width/2,height/2,image=roomsimgs[0])
window.wm_attributes('-transparentcolor','#add123')
window.geometry("1920x1080")



ismenu =True

#Matches key presses with directions
orientations={87:(1,-1),#W
              65:(0,-1),#A
              83:(1,1),#S
              68:(0,1)}#D
#Matches arrow presses with directions
arrows={
    37:(0,-1),#←
    38:(1,-1),#↑
    39:(0,1),#→
    40:(1,1)#↓    
}
shooting = False
#directions=[(0,1),(1,0),(0,-1),(-1,0)]

#Directions to add or remove to rooms in order to move
directions=[(0,-1),(-1,0),(0,1),(1,0)]

#Fixed door positions
door_positions=([width/2,room_ybound],[room_xbound-4.9,height/2],[width/2,height-room_ybound+15],[width-room_xbound-10.5,height/2])
#Fixed powerup positions
powerup_positions=[[360,500],[960,500],[1560,500]]

#Fonts
fonT = font.Font(size=50,family="hooge 05_55")
titleFont= font.Font(size=100,weight="bold",family="hooge 05_55")
smallfont = font.Font(size=35,family="hooge 05_55")


def kill_enemy(object):
    """
    When killing an enemy removes it and rolls to generate nothing, a coin or an heart
    """
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
    CHECKS IF A IS INSIDE B
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
    """
    Given an enemy checks all of the possible collisions.
    0 is no collision
    1 is collision with a non solid object
    2 is collision with a solid object
    """
    #if theres a collision with one of the players tears
    for tear in Giova.tears:
            if detect_collision(tear,self):
                #takes damage
                self.hp-=Giova.damage
                tear.die()
                return 1
    #if theres a collision with another enemys tear
    for tear in world.currentroom.enemy_tears:
        if detect_collision(tear,self):
            tear.die()
            return 1
    #if theres a collision with the player
    if detect_collision(Giova,self):
        return 2
    #if theres a collision with an object
    for object in world.currentroom.environment:
        if detect_collision(object,self):
            return 2
    for enemy in world.currentroom.enemies:
        #if the enemy is different from the one we are checking for and theres a collision with another enemy
        if enemy!=self and detect_collision(enemy,self):
            return 2
    return 0
        
def rotate(self,deg):
    """
    Rotates the doors based on their directions
    """
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
        # Creates a canvas for the menu background
        self.menubg = tk.Canvas(width=width, height=height, bg="Black")
        # Places the background image in the center of the canvas
        self.sfondo = self.menubg.create_image(width/2, height/2, image=roomsimgs[0])
        # Displays the game title at the top of the menu
        self.title = self.menubg.create_text(width/2, 300, text="The Binding Of Giova", font=titleFont, fill="#FEFAE0")
        
        # Creates the "Start" button
        self.playbtn = tk.Button(window, text="Start", command=self.play, relief="ridge", width=50, height=2, font=fonT, bg="#386641", activebackground="#6a994e", fg="#FEFAE0")
        # Creates the "Quit" button
        self.quitbtn = tk.Button(window, text="Quit", command=sys.exit, relief="ridge", font=fonT, bg="#386641", activebackground="#6a994e", fg="#FEFAE0")
        # Dimensions for the buttons
        self.xbound = 800
        self.ybound = 100
        # Places the buttons and background on the window
        self.place()
        
    def place(self):
        """Positions the menu background and buttons on the screen"""
        self.menubg.place(x=0, y=0)
        self.playbtn.place(x=width/2-self.xbound/2, y=500, width=self.xbound, height=self.ybound)
        self.quitbtn.place(x=width/2-self.xbound/2, y=650, width=self.xbound, height=self.ybound)
    
    def play(self):
        """When start is clicked"""
        #sets menu to false
        global ismenu
        ismenu = False
        
        # Destroy the menu components
        self.die()
        pass
    
    def die(self):
        # Destroys the menu canvas and buttons
        self.menubg.destroy()
        self.playbtn.destroy()
        self.quitbtn.destroy()



        
class player():
    def __init__(self):
        #current direction
        self.direction = [0,0]
        #previous direction
        self.lastdir= [0,0]
        #current position
        self.pos = [width/2,height/2]
        #speed
        self.speed = 5 
        #holds active tear objects
        self.tears=[]
        #current hp
        self.hp=3
        #holds active heart images
        self.hearts=[]
        #max hp
        self.max_hp=6
        #timer to not spam tears
        self.maxteartimer=10
        self.teartimer=0
        #player dimensions
        self.ybound=100
        self.xbound=100
        #invincibility timer
        self.invincibility_timer=0
        self.maxinvincibility_timer=10
        #damage dealt
        self.damage = 3
        #coins held
        self.coins=0
        #creates text and an icon for coins
        self.coinslabel = bg.create_text(1800,60,text=f"x{self.coins}",font=smallfont,fill="#FEFAE0")
        self.coinicon=bg.create_image(1730,50,image=coinimg,anchor='nw')
        #initializes a sprite
        self.Giovaimg = ImageTk.PhotoImage(Image.open("front.png").resize((self.xbound,self.ybound)))
        #places the sprite based on the position
        self.player_geometry = bg.create_image(self.pos[0],self.pos[1],image=self.Giovaimg,anchor='nw') 
        #creates hearts
        self.draw_hearts()
        self.init_draw()
        
    def init_draw(self):
        """
        Draws a new frame for the player and deletes the previous one
        """
        bg.delete(self.player_geometry)
        self.player_geometry = bg.create_image(self.pos[0],self.pos[1],image=self.Giovaimg,anchor='nw')
    def update_state(self):
        
        #gets the previous position and the previous direction
        oldpos=self.pos.copy()
        self.lastdir=self.direction.copy()
        #If going diagonally uses pythagoras's theorem
        if self.direction[0]&self.direction[1]:
            self.pos = [self.pos[0]+self.direction[0]*self.speed*math.sqrt(2)/2,self.pos[1]+self.direction[1]*self.speed*math.sqrt(2)/2]
        #otherwise moves normally
        else:
            self.pos = [self.pos[0]+self.direction[0]*self.speed,self.pos[1]+self.direction[1]*self.speed]
        #gets the change in position
        delta=[self.pos[0]-oldpos[0],self.pos[1]-oldpos[1]]
        #if theres a change updates the players sprite
        if delta[0]!=0 or delta[1]!=0:
            bg.moveto(self.player_geometry,self.pos[0],self.pos[1])
        #if you cant shoot tears updates the timer
        if self.teartimer<self.maxteartimer:
            self.teartimer+=1
        #if theres a collision with something or youre out of bounds sets the position to the previous one
        if self.detect_collisions()==2 or(self.pos[0]<room_xbound) or(self.pos[1]<room_ybound) or (self.pos[0]+self.xbound>width-room_xbound) or (self.pos[1]+self.ybound>height-room_ybound+12):
            self.pos=oldpos

        print(self.invincibility_timer)
        #if the invincibility timer gets to the max value sets it to zero
        if self.invincibility_timer==self.maxinvincibility_timer-1:
            self.invincibility_timer=0
        #otherwise if its more then zero updates the timer
        if self.invincibility_timer>0:

            self.invincibility_timer+=1
    def detect_collisions(self):
        
        """
        Detects collisions with enemies,objects,enemy tears,powerups,coins,hearts
        0 is no collsion
        1 is with a non solid object
        2 is with a solid object
        """
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
                return 1
        for coin in world.currentroom.coins:
            if detect_collision(coin,self):
                
                coin.die()
                self.coins+=1
                #updates the coin counter
                self.updateCoins()
                return 1
        for heart in world.currentroom.hearts:
            if detect_collision(heart,self):
                #if the players hp is lower than the maximum allowed 
                if self.hp<self.max_hp:
                    heart.die()
                    self.hp+=1
                    #updates the hearts on screen
                    self.draw_hearts()
                return 1
        #if theres a boss checks collision with it
        if world.currentroom.type=="boss":
            boss=world.currentroom.boss
            if detect_collision(self,boss.left_hand) or detect_collision(self,boss.right_hand) or detect_collision(self,boss.head):
                self.take_damage(1)

                return 2
        #otherwise returns zero
        return 0
    def take_damage(self,damage):
        #if the invincibility timer is zero, the player can take damage
        if self.invincibility_timer==0:
            #if out of hp close the game and show a game over message
            if self.hp==0:
                messagebox.showinfo("The Binding of Giova","Sei Morto")
                sys.exit()
            else:
                #otherwise lowers the players hp
                self.hp-=damage
                #sets the invincibility timer to 1 so it can tick up to the max value
                self.invincibility_timer=1
                #deleates the last heart
                bg.delete(self.hearts[-1])
                #removes it from the heart images
                self.hearts.pop()

    def Door_Move(self,direction):
        """
        Moves the player in the next room based on the position of the door he entered through.
        """
        #margin so the player doesnt collide with the door again
        margin=50
        #door dimensions
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
        """
        Draws heart icons on the screen
        """
        # Starting x position for drawing hearts
        self.posx = 50  
        # Clears existing heart icons before redrawing
        for i in self.hearts:
            bg.delete(i)
        # Resets the list of heart icons
        self.hearts = []  
        # For each point of health, draw a heart icon and add it to the list
        for i in range(self.hp):
            heart = bg.create_image(self.posx, 50, image=heartimg, anchor='nw')
            self.hearts.append(heart)
            # Moves the position for the next heart icon
            self.posx += 50  

    def updateCoins(self):
        """
        Updates the coin count display on the screen. It deletes the old display and creates a new one with the updated coin count
        """
        # Deletes the old coin count text
        bg.delete(self.coinslabel)  
        # Creates new text with the updated coin count
        self.coinslabel = bg.create_text(1800, 60, text=f"x{self.coins}", font=smallfont, fill="#FEFAE0")

        
    

class Tear():
    def __init__(self):
        self.direction=[0,0]
        self.pos=Giova.pos.copy()
        self.speed=10
        #this timer makes it so the tears dont go on forever
        self.timer=100
        self.xbound=10
        self.ybound=10
        #the tear inherits some of the players momentum
        self.momentum=[Giova.direction[0]*1.5,Giova.direction[1]*1.5]
        self.init_draw()

    def init_draw(self):
        #draws the tears
        self.tear_geometry = tk.Canvas(window,bg="cyan",height=self.ybound,width=self.xbound)
    def update_state(self):
        #decreases the timer
        self.timer-=1
        #if its zero deletes the tears
        if self.timer<=0:
            self.die()
        #otherwise updates their position
        else:
            self.pos = [self.pos[0]+self.direction[0]*self.speed+self.momentum[0],self.pos[1]+self.direction[1]*self.speed+self.momentum[1]]
            self.tear_geometry.place(x=self.pos[0],y=self.pos[1])
            #if the tears go out of bounds
            if (self.pos[0]<room_xbound) or(self.pos[1]<room_ybound) or (self.pos[0]+self.xbound>width-room_xbound) or (self.pos[1]+self.ybound>height-room_ybound+12):
                self.die()
            #for each obstacle checks the collision
            for obj in world.currentroom.environment:
                if detect_collision(self,obj)and self in Giova.tears:
                    self.die()

    def die(self):
            #removes the tears from the list of active tears
            Giova.tears.remove(self)
            #deleates them from the screen.
            self.tear_geometry.place_forget()
            self.tear_geometry.delete()
            self.tear_geometry.destroy()



class Enemy_Tear():
    """
    Almost the same as a player tear
    """
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
        #enemy dimensions
        self.ybound=100
        self.xbound=100
        #timer to shoot tears initialized at a random value to not sync up enemies
        self.timer=random.randint(1,99)
        #timer reset value
        self.timerdefault=random.randint(80,120)
        self.hp=4
        #placeholder for the enemy image
        self.enemy_geometry = None
    def update_state(self):
        # Checks if the enemy is dead
        if self.hp<=0:
            kill_enemy(self)
        else:
            
            self.detect_collisions()
            #decrements the shooting timer
            self.timer-=1
            #if its zero shoots a tear in the players direction
            if self.timer==0:
                dir = [Giova.pos[0]-self.pos[0],Giova.pos[1]-self.pos[1]]
                newtear=Enemy_Tear()
                newtear.pos=[self.pos[0]+self.xbound/2,self.pos[1]+self.ybound/2]
                newtear.direction = normalize_vector(dir)
                #adds the tear to the list of tears
                world.currentroom.enemy_tears.append(newtear)
                
                
                self.timer=self.timerdefault
        
    def detect_collisions(self):
        """
        Detects collisions with player's tears
        """
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
        self.hp=10
        #enemy image
        self.enemy_geometry = bg.create_image(self.pos[0],self.pos[1],image=followenemy_img,anchor='nw')


    def update_state(self):
        # Checks if the enemy is dead
        if self.hp<=0:
            kill_enemy(self)
        else:
            #Copies the current position
            oldpos=self.pos.copy()
            #Gets the direction towards the player
            dir = [Giova.pos[0]-self.pos[0],Giova.pos[1]-self.pos[1]]
            #normalizes it
            self.direction=normalize_vector(dir)
            #moves towards it
            self.pos= [self.pos[0]+self.direction[0]*self.speed,self.pos[1]+self.direction[1]*self.speed]
            #updates the image
            delta=[self.pos[0]-oldpos[0],self.pos[1]-oldpos[1]]
            #checks for collisions
            if delta[0]!=0 or delta[1]!=0:
                bg.moveto(self.enemy_geometry,self.pos[0],self.pos[1])
            if enemy_collisions(self)==2:
                self.pos=oldpos

class Random_Enemy():
    """
    A random enemy wouldnt have been challenging so this enemy is 
    semi-random, so it picks a direction and follows it for a set amount
    of time.
    """
    def __init__(self):
        self.direction=[0,0]
        self.speed = 6
        self.pos=[800,700]
        self.ybound=80
        self.xbound=80
        #timer for following a direction
        self.timer=random.randint(0,19)
        #reset value for the tmeir
        self.timerdefault=20
        self.hp=10
        """
        Given a direction on the x or y axis it multiplies it by 0.5, 0, 1, -1 or -0.5
        This is a placeholder for the x and y multipliers
        """
        self.random=[1,1]

        self.enemy_geometry = bg.create_image(self.pos[0],self.pos[1],image=randomenemy_img,anchor='nw')

    def update_state(self):
        #Checks if the enemy is alive
        if self.hp<=0:
            kill_enemy(self)
        else:
            self.timer-=1
            if self.timer<=0:
                self.timer=self.timerdefault
                #makes a random choice between the multipliers, with them being more skewed towards following the player
                self.random=random.choices(random_dir, weights=[3,2,7,8,7],k=2)
            oldpos=self.pos.copy()
            dir = [Giova.pos[0]-self.pos[0],Giova.pos[1]-self.pos[1]]
            #moves towards the player
            self.direction=normalize_vector(dir)
            self.pos= [self.pos[0]+self.direction[0]*self.speed*self.random[0],self.pos[1]+self.direction[1]*self.speed*self.random[0]]
            delta=[self.pos[0]-oldpos[0],self.pos[1]-oldpos[1]]
            #updates the sprite
            if delta[0]!=0 or delta[1]!=0:
                bg.moveto(self.enemy_geometry,self.pos[0],self.pos[1])
            #checks if its out of bounds or colliding with something (we need to check if out of bounds because it can go backwards)
            if enemy_collisions(self)==2 or(self.pos[0]<room_xbound) or(self.pos[1]<room_ybound) or (self.pos[0]+self.xbound>width-room_xbound) or (self.pos[1]+self.ybound>height-room_ybound+12):
                self.pos=oldpos

class Boss_main():
    
    def __init__(self):
        self.hp=150
        #timer for attacks
        self.timer=200
        self.timer_max=200 
        self.action=0
        
    def spawn(self):
        """the boss has an head and 2 arms. It spawns them, sets their images and positions
        """
        self.head=Boss_head()
        self.left_hand=Boss_hand()
        self.right_hand=Boss_hand()
        self.right_hand.pos=[1260,150]
        self.left_hand.hand_id=bg.create_image(self.left_hand.pos[0],self.left_hand.pos[1],image=l_hand_img,anchor='nw')
        self.right_hand.hand_id=bg.create_image(self.right_hand.pos[0],self.right_hand.pos[1],image=r_hand_img,anchor='nw')
        bg.tag_raise(self.right_hand.hand_id)
        bg.tag_raise(self.left_hand.hand_id)
    def update_state(self):
        #decreases the timer
        self.timer-=1
        if self.timer==0:
            #if the timer is zero deletes the current sprites and adds the default one
            bg.delete(self.head.head_id)
            self.head.head_id=bg.create_image(self.head.pos[0],self.head.pos[1],image=head_img,anchor='nw')
            #sets the timer back to 200 and picks a random attack
            self.timer=self.timer_max
            self.action=random.randint(1,5)
        match self.action:
            case 1: #shoots a random amount of tears across the screen
                #updates the animation every 25 frames
                if self.timer%25==0:
                    bg.delete(self.head.head_id)
                    #mod 8 since there 8 possible sprites. This is done to loop the animation
                    self.head.head_id=bg.create_image(self.head.pos[0],self.head.pos[1],image=netor_chad_imgs[(self.timer//25)%8],anchor='nw')
                if self.timer %50==0:
                    #divides the screen based on the number of tears and spaces them out evenly. 
                    tear_number=random.randint(8,14)
                    for i in range(tear_number):
                        enemy_tear=Enemy_Tear()
                        enemy_tear.pos=[width/tear_number*i,500]
                        #makes the tears come from the top and move downwards
                        enemy_tear.direction=[0,1]
                        world.currentroom.enemy_tears.append(enemy_tear)
            case 2: #changes the position of the left hand
                print("left hand")
                
                if self.timer>=80 and self.left_hand.pos[1]<580:#moves downwards
                    self.left_hand.pos[1]+=self.left_hand.speed
                elif self.timer>=80 and self.left_hand.pos[0]<1500:#moves right
                    self.left_hand.pos[0]+=self.left_hand.speed
                elif self.timer<=80 and self.left_hand.pos[0]>385:#moves back left
                    self.left_hand.pos[0]-=self.left_hand.speed
                elif self.timer<=80 and self.left_hand.pos[1]>150:#moves back up
                    self.left_hand.pos[1]-=self.left_hand.speed
                #actually moves the hand
                self.left_hand.update()
                
            case 3:#changes the position of the right hand
                print("right hand")
                if self.timer>=80 and self.right_hand.pos[1]<580:#moves downwards
                    self.right_hand.pos[1]+=self.right_hand.speed
                elif self.timer>=80 and self.right_hand.pos[0]>150:#moves left
                    self.right_hand.pos[0]-=self.right_hand.speed
                elif self.timer<=80 and self.right_hand.pos[0]<1260:#moves back right
                    self.right_hand.pos[0]+=self.right_hand.speed
                elif self.timer<=80 and self.right_hand.pos[1]>150:#moves back up
                    self.right_hand.pos[1]-=self.right_hand.speed
                self.right_hand.update()
            case 4: #shoots tears from the front
                #updates the animation
                if self.timer%25==0:
                    bg.delete(self.head.head_id)
                    self.head.head_id=bg.create_image(self.head.pos[0],self.head.pos[1],image=netor_scream_imgs[(self.timer//25)%8],anchor='nw')
                if self.timer %50==0:
                    #shoots 7 tears from the front, twice as fast
                    for i in range(7):
                        enemy_tear=Enemy_Tear()
                        enemy_tear.speed*=2
                        enemy_tear.pos=[760+66*i,500]
                        enemy_tear.direction=[0,1]
                        world.currentroom.enemy_tears.append(enemy_tear)
            case 5:#shoots some fast tears at the bottom, so that the player cant just stay still at the bottom.
                if self.timer%25==0:
                    bg.delete(self.head.head_id)
                    self.head.head_id=bg.create_image(self.head.pos[0],self.head.pos[1],image=netor_scream_imgs[(self.timer//25)%8],anchor='nw')
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
        #if the boss is dead shows a victory message
        messagebox.showinfo("The Binding of  Giova","Hai Vinto")
        sys.exit()
class Boss_head():
    def __init__(self):
       self.xbound=400
       self.ybound=400
       self.pos=[760,30]
       self.head_id=bg.create_image(self.pos[0],self.pos[1],image=head_img,anchor='nw')
    

class Boss_hand():
    def __init__(self):
        self.xbound=250
        self.ybound=250
        self.pos=[385,150]
        self.speed=20
        self.hand_id=None
    def update(self):
        """
        Changes the postion of the hand when attacking
        """
        bg.moveto(self.hand_id,self.pos[0],self.pos[1])

class Wall():
    def __init__(self):
        self.pos=[300,500]
        self.ybound=100
        self.xbound=100
        self.enemy_geometry = bg.create_image(self.pos[0],self.pos[1],image=rockimg,anchor='nw')
    def update(self):
        bg.delete(self.enemy_geometry)
        self.enemy_geometry = bg.create_image(self.pos[0],self.pos[1],image=rockimg,anchor='nw')
    def die(self):
        """
        Used to delete the wall when changing room
        """
        bg.delete(self.enemy_geometry)
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
    #gets the input from the player
    pressed=event.keycode
    #if its in W, A, S, D
    if pressed in orientations:
        #gets the rotation associated with the number and sets it for the direction
        rotate=orientations[pressed]
        Giova.direction[rotate[0]]=rotate[1]        
        #if the player isnt shooting and updates its direction, updates its iamge
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
                    

    #if the player pressed an arrow key and the timer allows him to shoot tears      
    elif pressed in arrows and Giova.teartimer==Giova.maxteartimer:
        #resets the timer
        Giova.teartimer=0
        #spawns a new tears
        new_tear=Tear()
        spawn_tear(pressed,new_tear,Giova)
        #adds it to the current tears
        Giova.tears.append(new_tear)
        #changes the players image based on the direction
        match pressed:
            case 37:
                Giova.Giovaimg = ImageTk.PhotoImage(Image.open("sinistra.png").resize((Giova.xbound,Giova.ybound)))
            case 38:
                Giova.Giovaimg = ImageTk.PhotoImage(Image.open("back.png").resize((Giova.xbound,Giova.ybound)))
            case 39:
                Giova.Giovaimg = ImageTk.PhotoImage(Image.open("destra.png").resize((Giova.xbound,Giova.ybound)))
            case 40:
                Giova.Giovaimg = ImageTk.PhotoImage(Image.open("front.png").resize((Giova.xbound,Giova.ybound)))
    #updates the players sprite.
    Giova.init_draw()

def release(event):
    """
    Ran when letting go of a key
    """

    global shooting
    pressed=event.keycode
    #if the players lets go of a key updates his direction
    if pressed in orientations:
        rotate=orientations[pressed]
        Giova.direction[rotate[0]]=0
    #if the player lets go of an arrow key sets the shooting variable to false
    if pressed in arrows:
        shooting = False

def update():
    """
    Ran every frame,if not in the menu updates the states of the player, every enemy, every tear,every enemy tear, the boss and checks collision with doors.
    """

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
        #if there are no more enemies the room is cleared and the player can move to another room
        elif not world.currentroom.enemies:
            world.currentroom.cleared=True
    window.after(20,update)

#Player instance
Giova = player()


class PowerUp():
    def __init__(self):
        self.pos = [0,0]
        self.xbound= 100
        self.ybound=100
        #powerup type
        self.index=random.randint(0,2)
        #powerup text
        self.text=None
        #powerup price
        self.price=0
        
    def draw(self):
        """
        Creates the powerup icon and the price text if its above 0
        """
        self.geometry = bg.create_image(self.pos[0],self.pos[1],image=powerupimgs[self.index],anchor='nw') 
        if self.price>0:
            self.text=bg.create_text(self.pos[0]+self.xbound/2,self.pos[1]-30,text=self.price,font=smallfont,fill="#FEFAE0")
            

    def generate_powerup(self):
        #when picking up a powerup clears the room so the player cant go in and out to get infinite powerups
        world.currentroom.cleared=True
        #if the player has enough coins
        if Giova.coins>=self.price:
            Giova.coins-=self.price
            Giova.updateCoins()
            match self.index:
                case 0:#More damage
                    Giova.damage+=random.randint(1,4)
                    print(f"Damage:{Giova.damage}")
                case 1:
                    #Sets the player hp to the current max
                    Giova.hp=Giova.max_hp
                    #increases the max
                    Giova.max_hp+=1
                    #updates the hearts
                    Giova.draw_hearts()
                    print(f"HP:{Giova.hp}")
                case 2:#more speed
                    Giova.speed+=random.randint(1,3)
                    print(f"Speed:{Giova.speed}")
            self.die()

    def die(self):
        """
        Deletes the price and the corrisponding text (if theres one)
        """
        bg.delete(self.geometry)
        world.currentroom.power_up.remove(self)
        if self.price>0:
            bg.delete(self.text)

#options that can be chosen when generating a level
environment_options=[[Wall()],[]]

walls = []
#Walls placed horizontally
for i in range(3):
    # Creates a new wall instance
    wall = Wall()  
    # Sets the position of the wall
    wall.pos[0] = 500 + 500 * i  
    # Adds the wall to the list of walls
    walls.append(wall)  
# Adds this configuration as an environment option
environment_options.append(walls)  

# Resets the list for another configuration
walls = []
# Walls in the middle
for i in range(3):
    # Creates another wall instance
    wall = Wall()  
    # Positions the wall relative to room center
    wall.pos = [width / 2 - 150 + 100 * i, height / 2 - 50]  
    # Adds the new wall to the list
    walls.append(wall)  
 # Adds this configuration as another environment option
environment_options.append(walls) 
# Resets the list for another configuration
walls = []
#Diagonal walls
for i in range(2):
    wall = Wall()
    if i == 0:
        # Positions the first wall in the top-left 
        wall.pos = [width / 4, height / 4]  
    else:
         # Positions the second wall in the bottom-right 
        wall.pos = [3 * width / 4 - wall.xbound, 3 * height / 4 - wall.ybound] 
    walls.append(wall)
environment_options.append(walls)

#creates skewed walls in the middle
walls = []
# Vertical wall
wall = Wall()
wall.pos = [width / 2 - wall.xbound / 2, height / 2 - 250]
walls.append(wall)

# Horizontal wall top
wall = Wall()
wall.pos = [width / 2 - 150, height / 2 - 150]
walls.append(wall)

# Horizontal wall bottom
wall = Wall()
wall.pos = [width / 2 + 50, height / 2 + 50]
walls.append(wall)
environment_options.append(walls)



class Room():
    def __init__(self):
        #Defines which edges have doors
        self.doors=[None]*4
        #holds the actual door objects
        self.door_objects=[]
        #defines the enemies in a room
        self.enemies=[]
        #defines the powerups
        self.power_up=[]
        #defines the walls
        self.environment=[]
        #defines the tears
        self.enemy_tears=[]
        #defines the coins
        self.coins=[]
        #defines the hearts
        self.hearts=[]
        #if the room is cleread there are no enemies and the player can move to another room
        self.cleared=False
        #room coordinates from the start
        self.coordinates=(0,0)
        #room type
        self.type="normal"
        #wall placement
        self.env_type=random.choice(environment_options)
        #image used for the background
        self.roomimg = roomsimgs[random.randint(0,1)]
        #boss object
        self.boss=None
        #places the background
        bg.place(y=0,x=0)
    def generate_position(self, enemy):
        """
        Generates a random position for an enemy within bounds that avoid walls and other enemies
        """
        bound=300
        #sets the radom position
        enemy.pos= [random.randint(room_xbound+bound,width-room_xbound-bound), random.randint(room_ybound+bound,height-room_ybound-bound)]
        #iterates through walls and if theres a collisions starts over        
        for objectt in (self.environment):
            if (enemy==Follow_Enemy and detect_collision(enemy,objectt)) or detect_collision(enemy,objectt):
                self.generate_position(enemy)
                return      
        #does the same for enemies
        for objectt in self.enemies:
            if (enemy==Follow_Enemy and detect_collision(objectt,enemy)) or detect_collision(enemy,objectt):
                self.generate_position(enemy)
                return 
            

    def generate(self,world):
        """
        Generates everything in a room when entering it
        """
        
        global sfondo
        #removes the previous background (to add it later on)
        bg.delete(sfondo)
        #Spawns doors
        for i in range(4):
            #given a position if it has a door
            if self.doors[i]==1:
                #spawns and rotates it
                door=Door()
                door.pos=door_positions[i].copy()            
                rotate(door,i)
                door.direction=i
                
                """this is to avoid crashes. Copies the current coordinates and modifies them to get the type 
                of the adjacent room, and changes the door color based on it."""
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
                    #draws the door
                    door.spawn()
                    #appends it to the rooms door objects
                    self.door_objects.append(door)
            
        #spawns different things based on the room type
        match self.type:
            case "normal":
                #spawns a normal background
                sfondo = bg.create_image(width/2,height/2,image=self.roomimg)
                self.environment=self.env_type.copy()
                #spawns walls
                for obj in self.environment:
                    obj.update()
                #if the room isnt cleared spawns enemies
                if not self.cleared:
                    #generates the number of enemies
                    enemy_number=random.randint(2,5)
                    for i in range(enemy_number):
                        #generates the enemy type
                        enemy_type=random.randint(0,2)
                        #based on the type generates the instance
                        match enemy_type:
                            case 0:
                                enemy=Static_Enemy()
                                
                            case 1:
                                enemy=Follow_Enemy()
                            case 2:
                                enemy=Random_Enemy()
                        
                        self.generate_position(enemy)
                        #if its a static enemy draws the sprite here so it doesnt have to be updated, since it doesnt move.
                        if enemy_type==0:
                            enemy.enemy_geometry = bg.create_image(enemy.pos[0],enemy.pos[1],image=staticenemy_img,anchor='nw')
                        #adds it to the room enemies
                        self.enemies.append(enemy)

                    
            case "shop":#if its a shop
                #sets the background
                sfondo = bg.create_image(width/2,height/2,image=special_roomsimgs[0])
                #if the player hasnt entered the shop spawn 3 random powerups
                if not self.cleared:
                    for i in range(3):
                        #generates the price randomly
                        price=random.randint(3,7)
                        powerup = PowerUp()
                        #sets price and position
                        powerup.price=price
                        powerup.pos=powerup_positions[i]
                        powerup.draw()
                        #adds it to the room powerups
                        self.power_up.append(powerup)
                            
            case "boss":
                #sets the background
                sfondo = bg.create_image(width/2,height/2,image=special_roomsimgs[1])
                #spawns the boss
                self.cleared=False
                self.boss=Boss_main()
                self.boss.spawn()
                #spawns the player in the bottom of the room, to avoid him spawning on top of the boss
                Giova.Door_Move(2)
                
                
            case "treasure":
                #sets the background
                sfondo = bg.create_image(width/2,height/2,image=special_roomsimgs[2])
                if not self.cleared:
                    #spawns a random number of powerups
                    powNum= random.randint(1,2)
                    for i in range(powNum):
                        powerup = PowerUp()
                        powerup.pos=powerup_positions[i]
                        powerup.draw()
                        self.power_up.append(powerup)
                        print("spawned")
            case "start":
                #sets the starting screen
                sfondo = bg.create_image(width/2,height/2,image=special_roomsimgs[3])
        #draws the player last, in order for him to be above the background
        Giova.init_draw()
        #raises the players hearts, coin counter and coin icon above the background
        for i in Giova.hearts:
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
        """
        if the player goes into a door change the current room"""
        if world.currentroom.cleared ==True and detect_collision(Giova,self):
            
            world.newroom(self.direction)
            
    def die(self):
        world.currentroom.door_objects.remove(self)
        self.door_geometry.place_forget()
        self.door_geometry.delete()
        self.door_geometry.destroy()



class World():
    def __init__(self):
        #the max number of rooms
        self.max_rooms=random.randint(10,15)
        #the current number of generated rooms
        self.generated_rooms=1
        #the current number of boss rooms
        self.current_boss_rooms=0
        #the current number of powerup rooms
        self.current_treasure_rooms=0
        #the current number of shop rooms
        self.current_shop_rooms=0
        #a dictionary matching room coordinates to room object, with the start room already initialized
        self.rooms={(0,0):Room()}
        #rooms for which to generate doors
        self.frontier=[(0,0)]
        #the current room. Initialized to the start
        self.currentroom=self.rooms[(0,0)]
        #while the number of generated rooms is less than the max
        while self.generated_rooms<self.max_rooms:
            #if theres rooms in the frontier
            if self.frontier:
                #gets the last element from the frontier and removes it
                room_coordinates=self.frontier[-1]
                self.frontier.pop()
                #sets it to the current generating room
                current_room=self.rooms[room_coordinates]
                #The directions are: TOP,LEFT,BOTTOM,RIGHT
                for door_direction in range(4):
                    #creates doors in the current room
                    door_chance=random.randint(0,1)
                    #if it is a 0
                    if not current_room.doors[door_direction]:
                        #decides if to add a door
                        current_room.doors[door_direction]=door_chance
                        if door_chance==1:
                            #gets the coordinates of the adjacent room
                            newroom_coordinates=(room_coordinates[0]+directions[door_direction][0],room_coordinates[1]+directions[door_direction][1])
                            #if the room doesnt already exist generates it
                            if newroom_coordinates not in self.rooms:
                                #increases the counter
                                self.generated_rooms+=1
                                #gets random numbers for the room type
                                if self.current_boss_rooms==0:
                                    boss_chance=random.randint(1,5)
                                if self.current_treasure_rooms<=2:
                                    treasure_chance=random.randint(0,4)
                                if self.current_shop_rooms==0:
                                    shop_chance=random.randint(0,5)
                                
                                #gets a new room instance
                                newroom=Room()
                                #Adds it to the dictionary
                                self.rooms[newroom_coordinates]=newroom
                                """
                                To ENSURE we get a boss rooms if the current amount of generable rooms is 2 it automatically spawns it.
                                Otherwise it does a calculation increasing the probability based on the distance from the start.
                                """
                                if boss_chance+current_room.coordinates[0]+current_room.coordinates[1]>=10 or (self.max_rooms-self.generated_rooms<=2 and self.current_boss_rooms==0):
                                    print("boss at",newroom_coordinates)
                                    
                                    self.current_boss_rooms+=1
                                    #sets the new room type
                                    newroom.type="boss"
                                    #sets the boss chance to 0
                                    boss_chance=0
                                #Gets a random number for the treasure rooms
                                elif treasure_chance==4:
                                    print("treasure at",newroom_coordinates)
                                    self.current_treasure_rooms+=1
                                    newroom.type="treasure"
                                    treasure_chance=0
                                #does the same calculation as the boss for the shop
                                elif shop_chance+current_room.coordinates[0]+current_room.coordinates[1]>=4:
                                    print("shop at",newroom_coordinates)
                                    self.current_shop_rooms+=1
                                    newroom.type="shop"
                                    shop_chance=0
                                #otherwise generates a normal room
                                else:
                                    newroom.type="normal"
                                    self.frontier.append(newroom_coordinates)
                            #Sets the corrisponding door in the opposite room
                            self.rooms[newroom_coordinates].doors[(door_direction+2)%4]=1
                            #sets the coordinates
                            newroom.coordinates=newroom_coordinates
            #if there arent rooms in the frontier
            else:
                #gets all of the rooms
                rooms=list(self.rooms.keys())
                #picks a random room
                choice=random.choice(rooms)
                #if its a normal type of room adds it to the frontier
                if self.rooms[choice].type=="normal":
                    self.frontier.append(choice)
        #after its done generating sets the beginning rooms type
        self.currentroom.type="start"
        #generates it
        self.currentroom.generate(self)
        #prints stats
        print(f"rooms: {self.generated_rooms} shops{self.current_shop_rooms} treasures {self.current_treasure_rooms}")
    def newroom(self,direction):
        """
        Deletes everything in the current room and changes room
        """
        #this is to avoid crashes. copies the current coordinates and modifies them to get those of the new room
        print("direction",direction)
        coordinates_holder=copy.deepcopy(self.currentroom.coordinates)
        newroom_index=(coordinates_holder[0]+directions[direction][0],coordinates_holder[1]+directions[direction][1])
        #if the room exists deletes everything
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
            #sets the new room
            self.currentroom=self.rooms[newroom_index]
            #this is also to avoid weirdness. Sets the new room coordinates to those calculated above
            self.currentroom.coordinates=newroom_index
            #changes the player direction to that of the corrispoding room. 
            direction=(direction+2)%4
            #moves the player
            Giova.Door_Move(direction)
            #generates the new room
            self.currentroom.generate(self)
            

world=World()      
Menuobj =Menu()

update()
window.bind("<KeyPress>",input)
window.bind("<KeyRelease>",release)
window.mainloop()