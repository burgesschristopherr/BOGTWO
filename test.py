import tdl

#set screen size
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#size of actual game area
MAP_WIDTH = 80
MAP_HEIGHT = 45

#color of shit in the dungeon
color_dark_wall = (255, 0, 0)
color_dark_ground = (50, 50, 150)

LIMIT_FPS = 20 #idk why this needs to happen?


class Tile:
    #deals with map tiles
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        #For now, if a tile is blocked, you also can't see it. Could maybe change later?
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight

#create object for everything in game
class GameObject:
    #always a character on screen
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
    #moves based on input
    def move(self, dx, dy):
        if not my_map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy

    #draws position of argument
    def draw(self):
        con.draw_char(self.x, self.y, self.char, self.color)
    #clears old position of argument
    def clear(self):
        con.draw_char(self.x, self.y, " ", self.color, bg=None)

#creates the map (holy shit this is a simple way to do it)
def make_map():
    global my_map

    #below makes the map, but is essentially empty
    my_map = [[Tile(False)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

    my_map[30][22].blocked = True
    my_map[30][22].block_sight = True
    my_map[50][22].blocked = True
    my_map[50][22].block_sight = True

#this draws all objects based on the list variable
def render_all():
    for obj in objects:
        obj.draw()

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = my_map[x][y].block_sight
            if wall:
                con.draw_char(x, y, "#", fg=None, bg=color_dark_wall)
            else:
                con.draw_char(x, y, None, fg=None, bg=color_dark_ground)

    root.blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0) #root is the main game screen, I have no idea what blit does?

#reads key inputs
def handle_keys():

    user_input = tdl.event.key_wait() #I don't understand what this does?

    if user_input.key == "ENTER" and user_input.alt: #Fullscreen, enter/exit
        tdl.set_fullscreen(not tdl.get_fullscreen())
    elif user_input.key == "ESCAPE": #quit game
        return True

    if user_input.key == "UP":
        player.move(0, -1)
    elif user_input.key == "DOWN":
        player.move(0, 1)
    elif user_input.key == "LEFT":
        player.move(-1, 0)
    elif user_input.key == "RIGHT":
        player.move(1, 0)

tdl.set_font("arial10x10.png", greyscale=True, altLayout=True) #Uses a font I downlaoded from some website
con = tdl.Console(SCREEN_WIDTH, SCREEN_HEIGHT) #uses earlier variables to set sceren size
root = tdl.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="BOGTWO", fullscreen=False) #this is a hidden background console, I think to do some behid the scenes calculations
tdl.setFPS(LIMIT_FPS) #I guess FPS limit matters?

player = GameObject(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, "@", (255,255,255)) #Creates player represetned as an @ symbol
npc = GameObject(SCREEN_WIDTH//2 - 5, SCREEN_HEIGHT//2, "E", (255,255,0)) #Creates enemy using E symbol
objects = [npc, player] #these are all the objects in the game.

make_map()

while not tdl.event.is_window_closed(): #so this syntax is weird but closed() returns boolean.
    print("Go") #this prints to console in the background. Might be useful for messages.

    render_all() #call render function

    tdl.flush() #flush refreshes the screen

    for obj in objects: #this clears objects previous positions from screen
        obj.clear()

    #handle keys and exit game if needed
    exit_game = handle_keys()
    if exit_game:
        break
