from random import choice
from copy import deepcopy
from time import sleep
import pyglet
from sys import exit
from grid import Grid
from piezas import Piezas


class Tetris2nd(pyglet.window.Window):
    """A class to recreate the classic game Tetris"""

    def __init__(self, *args, **kwargs):
        """Initializing parameters"""
        super().__init__(*args, **kwargs)
        # Screen constants
        pyglet.gl.glClearColor(1, 1, 1, 0.0)
        pyglet.gl.glOrtho(0, self.width, 0, self.height, 0, 1000)
        self.set_minimum_size(1280, 720)

        # Playing some music
        self.theme = pyglet.media.load("Original Tetris theme (Tetris Soundtrack) (128 kbps).mp3")
        self.mediaplayer = pyglet.media.Player()
        self.mediaplayer.queue(self.theme)
        self.mediaplayer.volume = 0.3
        self.mediaplayer.loop = True
        self.mediaplayer.play()

        # Define the constants like the block size and the tetriminos coordinates and grid
        self.BLOCK_SIZE = self.height // 24
        self.piezas = Piezas(self)
        self.grid = Grid(self)

        # Animating some walking mega man
        # self.ani = pyglet.resource.animation('megaman-running-gif-1.gif')
        # self.ani_sprite = pyglet.sprite.Sprite(img=self.ani, x=(2 * self.BLOCK_SIZE),
                                               # y=(2 * self.BLOCK_SIZE))

        # Define the valid play area
        self.play_area = deepcopy(self.grid.initial_play_area)

        # Get the list of coordinates to draw the first instance of the tetrimino
        self.first_tetri = []
        # Get a random number to draw the first tetrimino
        self.seven_bag = [0, 1, 2, 3, 4, 5, 6]
        self.random_number = [0]
        # The batch that the list belongs to, to draw to the screen
        self.tetrimino_batch = pyglet.graphics.Batch()
        # The list of coordinates of the current tetrimino at play
        self.active_tetrimino = []
        # The openGL shapes that get added to the batch to draw to the screen
        self.tetrimino_rectangles = []

        # Function call to generate first tetrimino
        self.create_new_tetri(self.first_tetri)
        self.generate_tetrimino(self.first_tetri, self.active_tetrimino)

        # Store info about frozen tetriminos
        self.frozen_batch = pyglet.graphics.Batch()
        self.frozen_area = []
        self.frozen_area_color = []
        self.tetrimino_frozen_rect = []

        self.indice = None

        # A flag that activates to move your tetris
        self.fast_fall_flag = False
        self.move_left_flag = False
        self.move_right_flag = False

        # A function call to constantly to the various function that animate the game
        pyglet.clock.schedule_interval(self.convert_to_rectangles_dyn, 1 / 60.0, self.active_tetrimino,
                                       self.tetrimino_rectangles, self.tetrimino_batch,
                                       self.random_number)
        pyglet.clock.schedule_interval(self.auto_move_down, 1 / 1.0, self.active_tetrimino, self.random_number)
        pyglet.clock.schedule_interval(self.fast_fall, 1 / 30.0, self.active_tetrimino)
        pyglet.clock.schedule_interval(self.move_left, 1 / 15.0, self.active_tetrimino)
        pyglet.clock.schedule_interval(self.move_right, 1 / 15.0, self.active_tetrimino)

    def create_new_tetri(self, tetri_piece_coordinates):
        """Randomly selects a tetri piece and gives its coordinates"""
        if len(self.seven_bag) == 0:
            for i in range(7):
                self.seven_bag.append(i)
        x = choice(self.seven_bag)
        self.random_number[0] = x
        self.seven_bag.remove(x)
        tetri_piece_coordinates.clear()
        for i in self.piezas.main_tetrimino[self.random_number[0]]:
            tetri_piece_coordinates.append(i)

    def convert_to_rectangles_dyn(self, dt, tetrimino_coordinates, opengl_rect_list,
                                  draw_batch, color_number):
        """Turns the tetrimino coordinates into openGL rectangles of the pieces that moce"""
        opengl_rect_list.clear()
        for i in tetrimino_coordinates:
            rectangles = pyglet.shapes.BorderedRectangle((i[0] * 30) + 490, (i[1] * 30) + 60, 30, 30, border=1,
                                                         border_color=(1, 1, 1), batch=draw_batch)
            rectangles.color = self.piezas.tetrimino_colors[color_number[0]]
            opengl_rect_list.append(rectangles)

    def convert_to_rectangles_frozen(self, tetrimino_coordinates, opengl_rect_list,
                                     draw_batch, color_number, clear_blocks=False):
        """Turns the tetrimino coordinates into openGL rectangles of the pieces that don't move"""
        if clear_blocks is True:
            opengl_rect_list.clear()
        for i, j in zip(tetrimino_coordinates, color_number):
            rectangles = pyglet.shapes.BorderedRectangle((i[0] * 30) + 490, (i[1] * 30) + 60, 30, 30, border=1,
                                                         border_color=(1, 1, 1), batch=draw_batch)
            rectangles.color = self.piezas.tetrimino_colors[j[0]]
            opengl_rect_list.append(rectangles)

    def generate_tetrimino(self, tetrimino_coordinates, activ_tetri_list, ):
        """Change tetrimino coordinates to appear at the top-center of the screen."""
        activ_tetri_list.clear()
        for i in tetrimino_coordinates:
            on_top = [i[0] + 5, i[1] + 20]
            activ_tetri_list.append(on_top)

    def future_position(self, tetrilist_to_move, side='down'):
        """Checks the future position of the tetrimino and returns false if it is an invalid move"""
        increment = -1
        axis = 1
        if side == "left":
            increment = -1
            axis = 0
        elif side == "right":
            increment = 1
            axis = 0
        elif side == 'down':
            pass
        copied_list = deepcopy(tetrilist_to_move)
        for i in copied_list:
            i[axis] += increment
            if i not in self.play_area or i in self.frozen_area:
                return False

    def game_over(self):
        """Function to check if the blocks can no longer move and end the game"""
        # stukc here
        if self.active_tetrimino[0][1] == 20 and self.future_position(self.active_tetrimino) is False:
            print("This is truly game over")

    def line_check_and_clear(self):
        """Function to check the lines if full, clear and the move the higher blocks down"""
        no_full_rows = 0
        lista_yaxis = []
        for i in range(21):
            filled_row = []
            for j in range(10):
                x = [j, i]
                if x in self.frozen_area:
                    filled_row.append(x)
            no_full_rows = self._line_clear(filled_row, lista_yaxis, no_full_rows)
        self._move_lines_down(lista_yaxis, no_full_rows)

    def _move_lines_down(self, lista_yaxis, no_full_rows):
        """Function to moves the higher pieces down after a line has been cleared"""
        if no_full_rows > 0:
            min_yaxis = min(lista_yaxis)
            for z in self.frozen_area:
                if z[1] > min_yaxis:
                    z[1] -= no_full_rows
        self.convert_to_rectangles_frozen(self.frozen_area, self.tetrimino_frozen_rect, self.frozen_batch,
                                          self.frozen_area_color, clear_blocks=True)

    def _line_clear(self, filled_row, lista_yaxis, no_full_rows):
        """Function to clear a line that has beed filled"""
        if len(filled_row) > 9:
            no_full_rows += 1
            lista_yaxis.append(filled_row[0][1])
            for w in filled_row:
                indice = self.frozen_area.index(w)
                self.frozen_area.pop(indice)
                self.frozen_area_color.pop(indice)
        return no_full_rows

    def draw_frozen_tetrimino(self, tetrilist_to_freeze, color):
        """Freeze the tretrimino when it hits the lowest possible position of the play area"""
        x = deepcopy(tetrilist_to_freeze)
        y = deepcopy(color)
        for i in x:
            self.frozen_area.append(i)
        for j in range(4):
            self.frozen_area_color.append(y)
        self.convert_to_rectangles_frozen(self.frozen_area, self.tetrimino_frozen_rect, self.frozen_batch,
                                          self.frozen_area_color)
        self.create_new_tetri(self.first_tetri)
        self.generate_tetrimino(self.first_tetri, self.active_tetrimino)

    def auto_move_down(self, dt, tetrilist_to_movedown, color):
        """main gameplay mechanic, auto drops the tetrimino 'gravity' basically."""
        if self.future_position(tetrilist_to_movedown) is False:
            self.draw_frozen_tetrimino(tetrilist_to_movedown, color)
            self.game_over()
            self.line_check_and_clear()
            return
        for i in tetrilist_to_movedown:
            i[1] -= 1

    def perform_valid_rotation(self, rotatable_tetri):
        """Checks if there is space to do a rotation and then does it"""
        x = deepcopy(rotatable_tetri)
        self.piezas.tetri_rotation(x, self.random_number)
        for i in x:
            if i not in self.play_area or i in self.frozen_area:
                return
        self.piezas.tetri_rotation(rotatable_tetri, self.random_number)

    def move_left(self, dt, tetrilist_to_moveleft):
        """The function to move the tetrimino to the left."""
        if self.future_position(tetrilist_to_moveleft, "left") is False:
            return
        else:
            pass
        if self.move_left_flag is True:
            for i in tetrilist_to_moveleft:
                i[0] -= 1

    def move_right(self, dt, tetrilist_to_moveright):
        """The function to move the tetrimino to the right"""
        if self.future_position(tetrilist_to_moveright, "right") is False:
            return
        else:
            pass
        if self.move_right_flag is True:
            for i in tetrilist_to_moveright:
                i[0] += 1

    def fast_fall(self, dt, tetrilist_to_movedown):
        """The function to make the tetrimino drop faster"""
        if self.future_position(tetrilist_to_movedown) is False:
            return
        else:
            pass
        if self.fast_fall_flag is True:
            for i in tetrilist_to_movedown:
                i[1] -= 1

    def on_key_press(self, symbol, modifiers):
        """Determine the functions on key press"""
        if symbol == pyglet.window.key.UP:
            self.perform_valid_rotation(self.active_tetrimino)
        if symbol == pyglet.window.key.LEFT:
            self.move_left_flag = True
        if symbol == pyglet.window.key.RIGHT:
            self.move_right_flag = True
        if symbol == pyglet.window.key.DOWN:
            self.fast_fall_flag = True
        if symbol == pyglet.window.key.ESCAPE:
            exit()

    def on_key_release(self, symbol, modifiers):
        """Determine the function of key releases"""
        if symbol == pyglet.window.key.LEFT:
            self.move_left_flag = False
        if symbol == pyglet.window.key.RIGHT:
            self.move_right_flag = False
        if symbol == pyglet.window.key.DOWN:
            self.fast_fall_flag = False

    def on_draw(self):
        """Draw to the screen"""
        self.clear()
        # self.ani_sprite.draw()
        self.grid.grid_batch.draw()
        self.tetrimino_batch.draw()
        self.frozen_batch.draw()

    def on_resize(self, width, height):
        pyglet.gl.glViewport(0, 0, width, height)


if __name__ == "__main__":
    t_game = Tetris2nd(1280, 720, caption="Tetris!!!", vsync=True, resizable=True)
    pyglet.app.run()
