import pyglet
from copy import deepcopy

class Piezas:
    def __init__(self, game):
        # Define the constants like the block size and the tetriminos coordinates and grid
        self.O = [[0, 0], [-1, 1], [-1, 0], [0, 1]]
        self.I = [[0, 0], [-2, 0], [-1, 0], [1, 0]]
        self.T = [[0, 0], [-1, 0], [0, 1], [1, 0]]
        self.S = [[0, 0], [-1, 0], [0, 1], [1, 1]]
        self.Z = [[0, 0], [-1, 1], [0, 1], [1, 0]]
        self.L = [[0, 0], [-1, 0], [1, 0], [1, 1]]
        self.J = [[0, 0], [-1, 1], [-1, 0], [1, 0]]
        self.main_tetrimino = {0: self.O, 1: self.I, 2: self.T, 3: self.S,
                               4: self.Z, 5: self.L, 6: self.J}
        self.tetrimino_colors = {0: (255, 255, 0), 1: (0, 255, 255), 2: (255, 0, 255), 3: (0, 255, 0),
                                 4: (255, 0, 0), 5: (255, 128, 0), 6: (0, 0, 255)}

    def tetri_rotation(self, tetrimino_to_rotate, selected_piece):
        """Function to rotate tetrimino 90deg to the right"""
        if selected_piece[0] == 0:
            return
        x = deepcopy(tetrimino_to_rotate[0])
        for i in tetrimino_to_rotate:
            i[0] -= x[0]
            i[1] -= x[1]
            y, z = - i[1], i[0]
            i[0], i[1] = (y + x[0]), (z + x[1])
