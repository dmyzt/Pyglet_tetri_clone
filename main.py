from random import choice
from copy import deepcopy
from time import sleep
from sys import exit

from pyglet.app import run
from pyglet.window import Window, key
from pyglet.media import Player, load
from pyglet.graphics import Batch
from pyglet.shapes import BorderedRectangle
from pyglet.clock import schedule_interval, schedule, schedule_once, unschedule
from pyglet.gl import glClearColor, glOrtho, glViewport
from pyglet.text import Label

from grid import Grid
from piezas import Piezas


class Tetris2nd(Window):
    """A class to recreate the classic game Tetris"""
    # Playing some music
    theme = load("Techno - Tetris (Remix) (128 kbps).mp3")
    mediaplayer = Player()
    mediaplayer.queue(theme)
    mediaplayer.volume = 0.1
    mediaplayer.loop = True
    mediaplayer.play()

    game_state_active = True
    pause_label = Label('Pause', font_name='Comic sans MS',
                        font_size=36, x=640, y=360, anchor_x='center', anchor_y='center', color=(255, 255, 0, 255))

    first_tetri = []  # Get the list of coordinates to draw the first instance of the tetrimino

    # Get a random number to draw the first tetrimino
    seven_bag = [0, 1, 2, 3, 4, 5, 6]
    random_number = [0]

    tetrimino_batch = Batch()  # The batch that the list belongs to, to draw to the screen
    active_tetrimino = []  # The list of coordinates of the current tetrimino at play
    tetrimino_rectangles = []  # The openGL shapes that get added to the batch to draw to the screen

    play_area = []  # Define the valid play area

    # Store info about frozen tetriminos
    frozen_batch = Batch()
    frozen_area = []
    frozen_area_color = []
    tetrimino_frozen_rect = []

    fast_fall_flag = False  # A flag to drop the pieces faster

    # Keeping track of the score
    rows_cleared = 0
    tetris_level = 1
    current_score = 0

    scoring_labels_batch = Batch()
    rows_cleared_label = Label(f'Lines: \n {rows_cleared}', font_name='Arial',
                               font_size=36, x=300, y=120, anchor_x='center', anchor_y='center',
                               multiline=True, width=100, color=(0, 192, 0, 255),
                               batch=scoring_labels_batch)
    level_label = Label(f'Lvl: \n {tetris_level}', font_name='Arial',
                        font_size=36, x=300, y=300, anchor_x='center', anchor_y='center',
                        multiline=True, width=100, color=(192, 0, 0, 255), batch=scoring_labels_batch)
    score_label = Label(f'Score: \n {current_score}', font_name='Arial',
                        font_size=36, x=1000, y=300, anchor_x='center', anchor_y='center',
                        multiline=True, width=100, color=(0, 0, 192, 255), batch=scoring_labels_batch)

    def __init__(self, *args, **kwargs):
        """Initializing parameters"""
        super().__init__(*args, **kwargs)
        # Screen constants
        glClearColor(0.9, 0.9, 1, 0.1)
        glOrtho(0, self.width, 0, self.height, 0, 1000)
        self.set_minimum_size(1280, 720)

        # importing the libraries
        self.piezas = Piezas(self)
        self.grid = Grid(self)

        # Fill the valid play area
        for i in range(0, 10, 1):
            for j in range(0, 25, 1):
                self.play_area.append([i, j])

        # Function call to generate first tetrimino
        self.create_new_tetri(self.first_tetri)
        self.generate_tetrimino(self.first_tetri, self.active_tetrimino)

        # A function call to constantly to the various function that animate the game
        schedule(self.convert_to_rectangles_dyn, self.active_tetrimino,
                 self.tetrimino_rectangles, self.tetrimino_batch, self.random_number)
        schedule(self.update_labels)
        self.gravity = schedule_interval(self.auto_move_down, 1 / 1, self.active_tetrimino,
                                         self.random_number)
        schedule_interval(self.fast_fall, 1 / 30, self.active_tetrimino)
        schedule_once(self.move_left, 1, self.active_tetrimino)
        schedule_once(self.move_right, 1, self.active_tetrimino)

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
            rectangles = BorderedRectangle((i[0] * 30) + 490, (i[1] * 30) + 60, 30, 30, border=1,
                                           border_color=(1, 1, 1), batch=draw_batch)
            rectangles.color = self.piezas.tetrimino_colors[color_number[0]]
            if i[1] > 19:
                rectangles.visible = False
            opengl_rect_list.append(rectangles)

    def convert_to_rectangles_frozen(self, tetrimino_coordinates, opengl_rect_list,
                                     draw_batch, color_number, clear_blocks=False):
        """Turns the tetrimino coordinates into openGL rectangles of the pieces that don't move"""
        if clear_blocks is True:
            opengl_rect_list.clear()
        for i, j in zip(tetrimino_coordinates, color_number):
            rectangles = BorderedRectangle((i[0] * 30) + 490, (i[1] * 30) + 60, 30, 30, border=1,
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
        increment, axis = -1, 1
        if side == "left":
            increment, axis = -1, 0
        elif side == "right":
            increment, axis = 1, 0
        elif side == 'down':
            pass
        copied_list = deepcopy(tetrilist_to_move)
        for i in copied_list:
            i[axis] += increment
            if i not in self.play_area or i in self.frozen_area:
                return False

    def game_over(self):
        """Function to check if the blocks can no longer move and end the game"""
        if self.active_tetrimino[0][1] >= 20 and self.future_position(self.active_tetrimino) is False:
            print("Game Over!!!")
            sleep(5)
            exit()

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

    def _line_clear(self, filled_row, lista_yaxis, no_full_rows):
        """Function to clear a line that has been filled"""
        if len(filled_row) > 9:
            no_full_rows += 1
            lista_yaxis.append(filled_row[0][1])
            for w in filled_row:
                indice = self.frozen_area.index(w)
                self.frozen_area.pop(indice)
                self.frozen_area_color.pop(indice)
        return no_full_rows

    def _move_lines_down(self, lista_yaxis, no_full_rows):
        """Function to move the higher pieces down after a line has been cleared"""
        self.update_score(no_full_rows)
        self.change_gravity()
        if no_full_rows > 0:
            min_yaxis = min(lista_yaxis)
            for z in self.frozen_area:
                if z[1] > min_yaxis:
                    z[1] -= no_full_rows
        self.convert_to_rectangles_frozen(self.frozen_area, self.tetrimino_frozen_rect, self.frozen_batch,
                                          self.frozen_area_color, clear_blocks=True)

    def update_score(self, no_rows):
        """Function the increase the score, number of lines cleared and current level"""
        self.rows_cleared += no_rows
        self.tetris_level = (self.rows_cleared // 10) + 1
        self.current_score += (no_rows * 40) * (no_rows * (self.tetris_level + 1))
        print(f"lines {self.rows_cleared}, level {self.tetris_level}, score {self.current_score}")

    def update_labels(self, dt):
        """Function to update scores on to the screen"""
        self.rows_cleared_label.text = f'Lines: \n {self.rows_cleared}'
        self.level_label.text = f'LvL: \n {self.tetris_level}'
        self.score_label.text = f'Score: \n {self.current_score}'

    def change_gravity(self):
        """Function to change the speed in where the pieces automatically fall"""
        if self.tetris_level <= 10:
            self.gravity = unschedule(self.auto_move_down)
            self.gravity = schedule_interval(self.auto_move_down, 1 / self.tetris_level, self.active_tetrimino,
                                             self.random_number)
        else:
            self.gravity = unschedule(self.auto_move_down)
            self.gravity = schedule_interval(self.auto_move_down, 1 / 11, self.active_tetrimino,
                                             self.random_number)

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

    def auto_move_down(self, dt, tetrilist_to_move_down, color):
        """main gameplay mechanic, auto drops the tetrimino 'gravity' basically."""
        if self.future_position(tetrilist_to_move_down) is False:
            self.draw_frozen_tetrimino(tetrilist_to_move_down, color)
            self.game_over()
            self.line_check_and_clear()
            return
        if self.game_state_active is True:
            for i in tetrilist_to_move_down:
                i[1] -= 1

    def perform_valid_rotation(self, rotatable_tetri):
        """Checks if there is space to do a rotation and then does it"""
        x = deepcopy(rotatable_tetri)
        self.piezas.tetri_rotation(x, self.random_number)
        for i in x:
            if i not in self.play_area or i in self.frozen_area:
                return
        self.piezas.tetri_rotation(rotatable_tetri, self.random_number)

    def move_left(self, dt, tetrilist_to_move_left):
        """The function to move the tetrimino to the left."""
        if self.future_position(tetrilist_to_move_left, "left") is False:
            return
        else:
            pass
        for i in tetrilist_to_move_left:
            i[0] -= 1

    def move_right(self, dt, tetrilist_to_move_right):
        """The function to move the tetrimino to the right"""
        if self.future_position(tetrilist_to_move_right, "right") is False:
            return
        else:
            pass
        for i in tetrilist_to_move_right:
            i[0] += 1

    def fast_fall(self, dt, tetrilist_to_move_down):
        """The function to make the tetrimino drop faster"""
        if self.future_position(tetrilist_to_move_down) is False:
            return
        else:
            pass
        if self.fast_fall_flag is True:
            for i in tetrilist_to_move_down:
                i[1] -= 1

    def on_key_press(self, symbol, modifiers):
        """Determine the functions on key press"""
        if symbol == key.UP:
            self.perform_valid_rotation(self.active_tetrimino)
        if symbol == key.LEFT:
            unschedule(self.move_right)
            self.move_left(None, self.active_tetrimino)
            schedule_interval(self.move_left, 0.15, self.active_tetrimino)
        if symbol == key.RIGHT:
            unschedule(self.move_left)
            self.move_right(None, self.active_tetrimino)
            schedule_interval(self.move_right, 0.15, self.active_tetrimino)
        if symbol == key.DOWN:
            self.fast_fall_flag = True
        if symbol == key.SPACE:
            self.game_state_active = not bool(self.game_state_active)
        if symbol == key.ESCAPE:
            exit()

    def on_key_release(self, symbol, modifiers):
        """Determine the function of key releases"""
        if symbol == key.LEFT:
            unschedule(self.move_left)
        if symbol == key.RIGHT:
            unschedule(self.move_right)
        if symbol == key.DOWN:
            self.fast_fall_flag = False

    def on_draw(self):
        """Draw to the screen"""
        self.clear()
        self.scoring_labels_batch.draw()
        self.grid.grid_batch.draw()
        self.tetrimino_batch.draw()
        self.frozen_batch.draw()
        if self.game_state_active is False:
            self.pause_label.draw()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)


if __name__ == "__main__":
    t_game = Tetris2nd(1280, 720, caption="Tetris!!!", vsync=True, resizable=True)
    run()
