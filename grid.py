import pyglet


class Grid:
    def __init__(self, game):
        self.grid_batch = pyglet.graphics.Batch()
        self.initial_grid = self.generate_rectangle(loc_batch=self.grid_batch)
        self.grid_list = []
        self.generate_grid()
        self.initial_play_area = []
        for i in range(0, 10, 1):
            for j in range(0, 25, 1):
                self.initial_play_area.append([i, j])

    def generate_grid(self):
        for x in range(0, 11 * 30, 30):
            for y in range(30 * 2, 23 * 30, 30):
                x_line = pyglet.shapes.Line(640 - (5 * 30), y,
                                            640 + (5 * 30),
                                            y, 1, (255, 255, 255), batch=self.grid_batch)
                y_line = pyglet.shapes.Line(640 - (5 * 30) + x, 30 * 2,
                                            640 - (5 * 30) + x, (30 * 22),
                                            1, (255, 255, 255), batch=self.grid_batch)
                x_line.opacity = 5
                y_line.opacity = 5
                self.grid_list.append(x_line)
                self.grid_list.append(y_line)

    def generate_rectangle(self, loc_batch=None):
        x = pyglet.shapes.Rectangle(640 - (5 * 30), 30 * 2,
                                    30 * 10, 30 * 20, (0, 0, 0),
                                    batch=loc_batch)
        return x
