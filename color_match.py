# This program is a simple matching game. When the player clicks on one of the two tiles, the tile will turn a random
# color, once both tiles have been activated in this way, the game check if the tiles are matching, if so, the player
# gains one "matching" score, otherwise, the player gains one "mismatching" score. The game ends when the player's
# mismatching score is equal to 5

# note, this program was written using my memory.py program as a framework, as I originally wrote it with versatility
# in mind and there is significant overlap in what needs to be done in each.


import pygame
import random
import time


# User-defined functions

def main():
    # initialize all pygame modules (some need initialization)
    pygame.init()
    # create a pygame display window
    pygame.display.set_mode((1200, 400))  # works best with tiles_per_row + 1 : tiles_per_column aspect ratio (3:1)
    # set the title of the display window
    pygame.display.set_caption('Color Match')
    # get the display surface
    w_surface = pygame.display.get_surface()
    # create a game object
    game = Game(w_surface)
    # start the main game loop by calling the play method on the game object
    game.play()
    # quit pygame and clean up the pygame window
    pygame.quit()


# User-defined classes
# tracks general gameplay specific features
class Game:
    # An object in this class represents a complete game.

    def __init__(self, surface):
        # Initialize a Game.
        # - self is the Game to initialize
        # - surface is the display window surface object

        # === objects and attributes that are part of every game that we will discuss
        self.surface = surface
        self.bg_color = pygame.Color('black')

        self.FPS = 60
        self.game_Clock = pygame.time.Clock()
        self.close_clicked = False
        self.continue_game = True

        # === objects and attributes that are only a part of color match

        # --- Match and mismatch score
        self.match_score = 0
        self.mismatch_score = 0

        # --- Tiles

        # find the spacing between tile coordinates needed
        tiles_per_row = 2
        tiles_per_column = 1
        spacing = 10
        space_between_tiles = find_tile_spacing(tiles_per_row, tiles_per_column, spacing, self.surface)

        # find the size of tiles needed
        dimensions = [space_between_tiles[0] - spacing, space_between_tiles[1] - spacing]

        # create a list containing the color codes for all the possible colors of the cards, and assign the hidden color
        self.colors = [pygame.Color("red"), pygame.Color("yellow"), pygame.Color("blue"), pygame.Color("green")]
        hidden_color = pygame.Color("white")

        # create all the tiles, and store them in a list

        # create one tile for each space on a grid by going through all possible x, y grid coordinate combinations
        self.deck = []

        for x in range(tiles_per_row):
            for y in range(tiles_per_column):

                # find the location of the tile by multiplying the tile spacing by the grid coordinate value for
                # the respective axis by it's tile spacing, then adding the space_between to prevent tiles touching
                location = [spacing + space_between_tiles[0] * x, spacing + space_between_tiles[1] * y]

                # create the tile for that spot on the grid before continuing to the next grid coordinate
                self.deck.append(Tile(dimensions, location, random.choice(self.colors), hidden_color, self.surface))

        # create an attribute to track tiles currently 'active' (not covered and not matched)
        self.active_tiles = []

    # score is an int containing the value of the score to be displayed
    # title is a string containing the title of the score

    # this method creates a surface displaying a score and the title of that score as "title: score"
    def scoreboard_render(self, score, title):
        # Text settings
        font_size = 60
        font = pygame.font.SysFont("arial", font_size)
        color = pygame.Color("white")

        # combine score and title
        titled_score = title + ": " + str(score)

        # render the score
        scoreboard = pygame.font.Font.render(font, titled_score, True, color)
        return scoreboard

    # this method handles the loop of all processes that occur every frame
    def play(self):
        # Play the game until the player presses the close box.
        # - self is the Game that should be continued or not.

        while not self.close_clicked:  # until player clicks close box
            # play frame
            self.handle_events()

            # if not yet at 5 mismatches
            if self.continue_game:
                self.decide_continue()
                self.draw()
                self.update()
            self.game_Clock.tick(self.FPS)  # run at most with FPS Frames Per Second

    # this method handles all action related to user input
    def handle_events(self):
        # get all inputs that have occurred since last check
        events = pygame.event.get()
        for event in events:

            # if the event was an attempt to close the game, flag the game to be closed
            if event.type == pygame.QUIT:
                self.close_clicked = True

            # if the event was a mouse click, check if a tile was clicked on and which one
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.click_check()

    # this method is responsible for drawing all graphical elements to the screen
    def draw(self):

        self.surface.fill(self.bg_color)  # clear the display surface first

        # draw tiles to screen
        for tile in self.deck:
            tile.draw()

        # draw scores to screen

        # update the scoreboards
        top_scoreboard = self.scoreboard_render(self.match_score, "Matched")
        bot_scoreboard = self.scoreboard_render(self.mismatch_score, "Mismatched")

        # draw scoreboards to screen
        self.surface.blit(top_scoreboard, (self.surface.get_size()[0] - top_scoreboard.get_size()[0], 0))
        self.surface.blit(bot_scoreboard, (self.surface.get_size()[0] - bot_scoreboard.get_size()[0], 50))

        pygame.display.update()  # make the updated surface appear on the display

    # this method is responsible for updating all game interactions that are not influenced directly by the player
    def update(self):

        # check if active cards are matching, and perform relevant actions if so or if not.
        self.match_check()

    # this method checks if the active tiles are matching, then increments the correlating score before resetting them
    def match_check(self):

        # check if more than one tile is active, if so, check if they match
        if len(self.active_tiles) > 1:
            tile1, tile2 = self.active_tiles
            pair = tile1.pair_check(tile2)

            # if the tiles match, increment match score by one, else increment mismatch score by one
            if pair:
                self.match_score += 1
            else:  # if not pair
                self.mismatch_score += 1

            # randomize the true colors of the tiles and flip them back to hidden regardless of if they matched or not
            tiles = [tile1, tile2]
            for tile in tiles:
                tile.color_change(random.choice(self.colors))
                tile.flip()

            # wait for 1 second before continuing, so that player can see the tiles colors
            time.sleep(1)

            # clear the tiles from the active tile list regardless
            self.active_tiles = []

    # this method is responsible for checking if the game has come to an end, if so, it marks continue_game as False
    def decide_continue(self):

        # game is over when mismatch score reaches 5, therefore check if mismatch score is equal to or greater than 5
        if self.mismatch_score >= 5:
            self.continue_game = False

    # this method should only be called when a mouse down event is detected. when called, it checks if the mouse
    # position is currently over any of the tiles, if so, it flips the tile and adds it to the active tile list
    def click_check(self):

        # check if mouse is colliding with any hidden tiles
        mouse_position = pygame.mouse.get_pos()
        for tile in self.deck:
            if tile.collision_check(mouse_position) and tile.check_hidden():

                # if so, flip tile and mark it as active
                tile.flip()
                self.active_tiles.append(tile)


# this class represents one tile in the color match game
# a tile has a front and a back side
# a tile can either be face up or face down
# a tile displays the color of the side that is currently up
# a tile is a rectangle of a specified size
# a tile is located at a specific location on the screen
class Tile:

    # dimensions is a list containing the dimensions of the tile in [width, height] format
    # location is a list containing the coordinates for the top left corner of the tile in [x, y] format
    # front_color is a color code for the color of the front side of the tile
    # hidden_color is a color code for the color of the back side of the tile
    # screen is the surface the tile will be drawn to
    def __init__(self, dimensions, location, front_color, hidden_color, screen):
        self.rect = pygame.Rect(location, dimensions)
        self.screen = screen
        self.hidden = True
        self.true_color = front_color
        self.hidden_color = hidden_color

    # this method is responsible for drawing the tile to the screen
    def draw(self):

        # if the tile is hidden (face-down) set the color to the backside, otherwise set the color to the front side
        if self.hidden:
            color = self.hidden_color
        else:  # if not self.hidden
            color = self.true_color

        # print the decided color to the screen at the location of the tile's rect
        pygame.draw.rect(self.screen, color, self.rect)

    # pos is a list or tuple containing coordinates

    # this method checks if the coordinates provided are in collision with the tile, if so, it returns true, else false
    def collision_check(self, pos):
        return self.rect.collidepoint(pos[0], pos[1])

    # this method, when called, toggles whether or not the tile is hidden
    def flip(self):
        self.hidden = not self.hidden

    # this method returns a boolean indicating if the tile is hidden (True) or revealed (False)
    def check_hidden(self):
        return self.hidden

    # this method returns the name of the true_color shown on the front of the card
    def get_color(self):
        return self.true_color

    # tile is an object containing information about the tile this tile is being checked against

    # this method checks if the tile provided has the same front_color as itself. if so, it returns True, else False
    def pair_check(self, tile):

        # get the colors to check
        other_color = tile.get_color()
        this_color = self.true_color

        # check if colors match, and return boolean true or false accordingly
        if this_color == other_color:
            match = True
        else:  # if this_color != other_color
            match = False
        return match

    # color is a pygame color code containing the color the tile should be changed to

    # This method changes the true color of the tile to the provided color
    def color_change(self, color):
        self.true_color = color


# tiles_per_row is an int containing the number of tiles that have to fit horizontally across the screen
# tiles_per_column is an int containing the number of tiles that have to fit vertically stacked on the screen
# space between is an int containing the size of the border between cards, in pixels
# screen is the surface the tile will later be printed to

# this function finds the necessary spacing between tile items coordinates in order to fit properly within the window
# it returns a list containing the necessary spacing in [x, y] format
def find_tile_spacing(tiles_per_row, tiles_per_column, space_between, screen):
    tiles_per_row += 1  # reserves a column of equal width to the rest for the score
    dimensions = list(screen.get_size())
    dimensions[1] = dimensions[1] - space_between  # this allows for spacing on bottom
    tile_spacing = [0, 0]  # needed to establish size of list, values here are irrelevant
    tile_spacing[0] = dimensions[0] // tiles_per_row
    tile_spacing[1] = dimensions[1] // tiles_per_column
    return tile_spacing


main()
