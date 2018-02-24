import tdl
from random import randint
import colors

#set screen size
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#size of actual game area
MAP_WIDTH = 80
MAP_HEIGHT = 45

#color of shit in the dungeon
color_dark_wall = (0, 0, 0)
color_dark_ground = (50, 50, 150)

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

MAX_ROOM_MONSTERS = 5

FOV_ALGO = "BASIC"
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

color_dark_wall = (0, 0, 100)
color_light_wall = (130, 110, 50)
color_dark_ground = (50, 50, 150)
color_light_ground = (200, 180, 50)



LIMIT_FPS = 20 #idk why this needs to happen?

class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Tile:
    #deals with map tiles
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        self.explored = False

        #For now, if a tile is blocked, you also can't see it. Could maybe change later?
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight

#create object for everything in game
class GameObject:
    #always a character on screen
    def __init__(self, x, y, char, name, color, blocks=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
    #moves based on input
    def move(self, dx, dy):
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    #draws position of argument
    def draw(self):
        global visible_tiles

        if (self.x, self.y) in visible_tiles:
            con.draw_char(self.x, self.y, self.char, self.color)
    #clears old position of argument
    def clear(self):
        con.draw_char(self.x, self.y, " ", self.color, bg=None)

def place_objects(room):
    num_monsters = randint(2, MAX_ROOM_MONSTERS)

    for i in range(num_monsters):
        x = randint(room.x1, room.x2)
        y = randint(room.y1, room.y2)
        if not is_blocked(x, y):
            if randint(0, 100) < 80:
                monster = GameObject(x, y, "o", "Orc", colors.desaturated_green, blocks=True) #orc
            else:
                monster = GameObject(x, y, "T", "Troll", colors.darker_green, blocks=True) #troll
            objects.append(monster)

def is_blocked(x, y):
    if my_map[x][y].blocked:
        return True

    for obj in objects:
        if obj.blocks and obj.x == x and obj.y == y:
            return True
    return False

def create_room(room):
    global my_map

    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1, room.y2 + 1):
            my_map[x][y].blocked = False
            my_map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    global my_map

    for x in range(min(x1, x2), max(x1, x2) + 1):
        my_map[x][y].blocked = False
        my_map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    global my_map

    for y in range(min(y1, y2,), max(y1, y2) + 1):
        my_map[x][y].blocked = False
        my_map[x][y].block_sight = False

def player_move_or_attack(dx, dy):
    global fov_recompute

    x = player.x + dx
    y = player.y + dy

    target = None
    for obj in objects:
        if obj.x == x and obj.y == y:
            target = obj
            break

    if target is not None:
        print("The {} Laughs at your puny efforts to attack him!" .format(target.name))
    else:
        player.move(dx, dy)
        fov_recompute = True

#creates the map (holy shit this is a simple way to do it)
def make_map():
    global my_map

    #below makes the map, but is essentially empty
    my_map = [[Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        w = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)

        x = randint(0, MAP_WIDTH-w-1)
        y = randint(0, MAP_HEIGHT-h-1)

        new_room = Rect(x, y, w, h)

        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            create_room(new_room)

            (new_x, new_y) = new_room.center()

            room_no = GameObject(new_x, new_y, chr(65+num_rooms), "room number", colors.white)
            objects.insert(0, room_no)

            if num_rooms == 0:
                player.x = new_x
                player.y = new_y

            else:
                (prev_x, prev_y) = rooms[num_rooms-1].center()

                if randint(0, 1):
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            place_objects(new_room)
            rooms.append(new_room)
            num_rooms += 1

def is_visible_tile(x, y):
    global my_map
    if x >= MAP_WIDTH or x < 0:
        return False
    elif y >= MAP_HEIGHT or y < 0:
        return False
    elif my_map[x][y].blocked == True:
        return False
    elif my_map[x][y].block_sight == True:
        return False
    else:
        return True

#this draws all objects based on the list variable
def render_all():
    global fov_recompute
    global visible_tiles

    if fov_recompute:
        fov_recompute = False
        visible_tiles = tdl.map.quickFOV(player.x, player.y,
                                        is_visible_tile,
                                        fov=FOV_ALGO,
                                        radius=TORCH_RADIUS,
                                        lightWalls=FOV_LIGHT_WALLS)

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            visible = (x, y) in visible_tiles
            wall = my_map[x][y].block_sight
            if not visible:
                if my_map[x][y].explored:
                    if wall:
                        con.draw_char(x, y, None, fg=None, bg=color_dark_wall)
                    else:
                        con.draw_char(x, y, None, fg=None, bg=color_dark_ground)
            else:
                if wall:
                    con.draw_char(x, y, "#", fg=None, bg=color_light_wall)
                else:
                    con.draw_char(x, y, None, fg=None, bg=color_light_ground)
                my_map[x][y].explored = True

    for obj in objects:
        obj.draw()



    root.blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0) #root is the invisible screen I have no idea what blit does?

#reads key inputs
def handle_keys():
    global fov_recompute

    user_input = tdl.event.key_wait() #I don't understand what this does?

    if user_input.key == "ENTER" and user_input.alt: #Fullscreen, enter/exit
        tdl.set_fullscreen(not tdl.get_fullscreen())

    elif user_input.key == "ESCAPE": #quit game
        return "exit"

    if game_state == "playing":
        if user_input.key == "UP":
            player_move_or_attack(0, -1)

        elif user_input.key == "DOWN":
            player_move_or_attack(0, 1)

        elif user_input.key == "LEFT":
            player_move_or_attack(-1, 0)

        elif user_input.key == "RIGHT":
            player_move_or_attack(1, 0)

        else:
            return "didnt-take-turn"



tdl.set_font("arial10x10.png", greyscale=True, altLayout=True) #Uses a font I downlaoded from some website
con = tdl.Console(SCREEN_WIDTH, SCREEN_HEIGHT) #uses earlier variables to set sceren size
root = tdl.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="BOGTWO", fullscreen=False) #this is a hidden background console, I think to do some behid the scenes calculations
tdl.setFPS(LIMIT_FPS) #I guess FPS limit matters?

player = GameObject(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, "@", "Player", colors.white, blocks=True) #Creates player represetned as an @ symbol
objects = [player] #these are all the objects in the game.

make_map()

fov_recompute = True
game_state = "playing"
player_action = None

while not tdl.event.is_window_closed(): #so this syntax is weird but closed() returns boolean.
    print("Go") #this prints to console in the background. Might be useful for messages.

    render_all() #call render function

    tdl.flush() #flush refreshes the screen

    for obj in objects: #this clears objects previous positions from screen
        obj.clear()

    #handle keys and exit game if needed
    player_action = handle_keys()
    if game_state == "playing" and player_action != "didnt-take-turn":
            for obj in objects:
                if obj != player:
                    print("The {} growls!" .format(obj.name))
    if player_action == "exit":
        break
#This is a comment that I, Larry, am making.
