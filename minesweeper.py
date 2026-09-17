import pygame
import sys
import random
from pathlib import Path

pygame.init()

# Save the settings related to the layout of our board

boardSize = 10
tileSize = 17

boardX = 25
boardY = 25

# controls difficulty and number of boms
## can change number of bombs, will always have this many bombs
max_num_of_bombs = 10
per_chance_bomb = 0.10 # weighted percent chance that a tile has a bomb

boardWidth = boardSize * tileSize
boardHeight = boardSize * tileSize

windowWidth = boardX + boardWidth + 10
windowHeight = boardY + boardHeight + 10

screen = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption("Minesweeper")

clock = pygame.time.Clock()

# Save a few basic colors

white = (255, 255, 255)
black = (0, 0, 0)

# Font used for text in the window

font = pygame.font.Font(None, 20)

# Save the images we'll reference for graphics

## Directory paths
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

coveredTile = pygame.image.load(ASSETS_DIR / "block.png")
selectedTile = pygame.image.load(ASSETS_DIR / "selblock.png")
blankTile = pygame.image.load(ASSETS_DIR / "blankblock.png")
flagImage = pygame.image.load(ASSETS_DIR / "flag.png")
bombImage = pygame.image.load(ASSETS_DIR / "bomb.png")

numbers = {
    1: pygame.image.load(ASSETS_DIR / "block1.png"),
    2: pygame.image.load(ASSETS_DIR / "block2.png"),
    3: pygame.image.load(ASSETS_DIR / "block3.png"),
    4: pygame.image.load(ASSETS_DIR / "block4.png"),
    5: pygame.image.load(ASSETS_DIR / "block5.png"),
    6: pygame.image.load(ASSETS_DIR / "block6.png"),
    7: pygame.image.load(ASSETS_DIR / "block7.png"),
    8: pygame.image.load(ASSETS_DIR / "block8.png")
}

# ---------------------------------------------------------------------------
# Create a class for our tiles
#
# State descriptions:
# -1 = the tile is still "covered"
# -2 = the tile has a flag on it
# -3 = the tile was clicked and has a bomb
# 0 = the tile has been clicked on and is revealed blank
# 1-8 = the tile has been clicked on and is revealed to have a number on it
# ---------------------------------------------------------------------------

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(
            boardX + x * tileSize,
            boardY + y * tileSize,
            tileSize,
            tileSize
        )

        self.state = -1
        self.has_bomb = False

# Create the board

board = [
    [Tile(x, y) for x in range(boardSize)]
    for y in range(boardSize)
]

# Sets bombs on the board
# iterates through board
# if can_place bomb
# place bomb
# display in console where the bombs arelocated

def set_bombs(board):
    curr_bombs = 0

    while curr_bombs < max_num_of_bombs:
        for row in board:
            for tile in row:
                if can_place_bomb(tile, curr_bombs):
                    tile.has_bomb = True
                    curr_bombs += 1
                    print("placed bomb at ", tile.x, " ", tile.y)
         
# Helper function
# determines if a bomb can be placed on a given tile
# checks if tile has bomb, continue
# generates random chance to place bomb, place bomb
## expand logic to not let player lose on first click later

def can_place_bomb(tile, curr_bombs) -> bool:
    if not tile.has_bomb:
        if get_rand_chance() <= per_chance_bomb:
            if curr_bombs < max_num_of_bombs:
                return True
    else:
        return False

# Helper function
# generates a random float between 0 and 1
## weighed against the percent chance variable above
### if roll below or equal to chance , place bomb
### else if roll above, no bomb

def get_rand_chance() -> float:
    return random.uniform(0.0, 1.0)

# Find what tile is under the mouse cursor

def getTile(mousePos):
    for row in board:
        for tile in row:
            if tile.rect.collidepoint(mousePos):
                return tile

    return None

set_bombs(board)

# Sets tile state to number of bombs surrounding
# iterates through all tiles around clicked tile
# if detects a bomb, increases tile state by 1
# uses code in main loop to display tile state

def set_tile_state(tile):
    board_grid_x = tile.x - 1
    board_grid_y = tile.y - 1

    print("In set_tile_state, tile is [", tile.x, ",", tile.y, "]")

    for x in range(3):
        for y in range(3):
            print("checking[", board_grid_x + x, ",", board_grid_y + y, "]")
            if is_valid_index(board_grid_x + x, board_grid_y + y):
                if board[board_grid_x + x][board_grid_y + y].has_bomb:
                    tile.state += 1
                    
                    print("Setting tilestate to: ", tile.state)

                    board_grid_x += 1
                    board_grid_y += 1

# helper function
# boolean function that determines if an index is valid or not

def is_valid_index(x, y) -> bool:
    if x >= boardSize or y >= boardSize:
        print("x/y greater than board limit returning false ")
        return False
    if x < 0 or y < 0:
        print("x/y is less than 0")
        return False
            
    print("returning true ")
    return True

# Draw the board for the user

def drawBoard(mouseTile):
    screen.fill(white)

    # Draw column labels from A - J on top of the board
    for x in range(boardSize):
        label = font.render(
            chr(ord('A') + x),
            True,
            black
        )

        labelRect = label.get_rect(
            center=(
                boardX + x * tileSize + tileSize // 2,
                boardY // 2
            )
        )

        screen.blit(label, labelRect)

    # Draw row labels from 1 - 10 on the left of the board
    for y in range(boardSize):
        label = font.render(
            str(y + 1),
            True,
            black
        )

        labelRect = label.get_rect(
            center=(
                boardX // 2,
                boardY + y * tileSize + tileSize // 2
            )
        )

        screen.blit(label, labelRect)

    for row in board:
        for tile in row:
            if tile.state == -1:
                if tile == mouseTile:
                    screen.blit(selectedTile, tile.rect)
                else:
                    screen.blit(coveredTile, tile.rect)

            elif tile.state == -2:
                screen.blit(flagImage, tile.rect)

            elif tile.state == -3:
                screen.blit(bombImage, tile.rect)

            elif tile.state == 0:
                screen.blit(blankTile, tile.rect)

            elif tile.state in numbers:
                screen.blit(
                    numbers[tile.state],
                    tile.rect
                )
# ----------
# Main loop
# ----------

mouseTile = None

while True:

    # Catch-all event tracker
    for event in pygame.event.get():

        # Closes the game window
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Keep track of which tile the mouse is currently over
        elif event.type == pygame.MOUSEMOTION:
            mouseTile = getTile(event.pos)

        # Check for mouse clicks, run if one is made
        elif event.type == pygame.MOUSEBUTTONUP:
            tile = getTile(event.pos)

            # Ignore mouse clicks that aren't on tiles
            if tile is None:
                continue

            # A left click on a covered tile reveals what's under it
            if event.button == 1:
                if tile.state == -1:
                    if tile.has_bomb == True:
                        tile.state = -3
                    else:
                        tile.state = 0
                        set_tile_state(tile)

            # A right click adds or removes a flag
            elif event.button == 3:
                if tile.state == -1:
                    tile.state = -2

                elif tile.state == -2:
                    tile.state = -1

    drawBoard(mouseTile)
    pygame.display.flip()
    clock.tick(60)
