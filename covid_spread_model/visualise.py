import pyglet


class Visualiser:
    COLOR_BLACK = (0, 0, 0)
    COLOR_DARKGREY = (100, 100, 100)
    COLOR_RED = (255, 0, 0)
    COLOR_GREEN = (0, 255, 0)
    COLOR_BLUE = (0, 0, 255)

    def __init__(self, config, graph, path):
        self.config = config
        self.graph = graph
        self.path = path
        self.window = pyglet.window.Window()
        self.on_draw = self.window.event(self.on_draw)
        # widths, heights
        self.unit_width = 2 + (self.config['num_aisles_horizontal'] * 3)
        self.unit_height = 3 + (self.config['num_aisles_vertical'] * (self.config['num_shelves_per_aisle'] + 1))
        self.pixels_per_unit = 50
        self.width = self.pixels_per_unit * self.unit_width
        self.height = self.pixels_per_unit * self.unit_height
        self.window.set_size(self.width, self.height)
        self.rects = []
        for x in range(self.unit_width):
            for y in range(self.unit_height):
                if self.is_start_door(x, y):
                    self.rects.append((x, y, self.COLOR_GREEN))
                elif self.is_end_door(x, y):
                    self.rects.append((x, y, self.COLOR_RED))
                elif self.is_wall(x, y):
                    self.rects.append((x, y, self.COLOR_BLACK))
                elif self.is_shelf(x, y):
                    self.rects.append((x, y, self.COLOR_DARKGREY))
    
    def is_wall(self, x, y):
        lx = self.unit_width - 1
        ly = self.unit_height - 1
        if x == 0 or x == lx or y == 0 or y == ly: return True
        if not self.is_shelf_y(y) and (x == 1 or x == lx - 1): return True
        return False

    def is_shelf(self, x, y):
        return self.is_shelf_x(x) and self.is_shelf_y(y)
    
    def is_shelf_x(self, x):
        return (x - 2) % 3 != 0
    
    def is_shelf_y(self, y):
        return (y - 1) % (self.config['num_shelves_per_aisle'] + 1) != 0

    def is_start_door(self, x, y):
        return x == 2 and y == 0
    
    def is_end_door(self, x, y):
        return x == self.unit_width - 3 and y == 0

    def run(self):
        pyglet.gl.glClearColor(1, 1, 1, 0)
        pyglet.app.run()
    
    def on_draw(self):
        self.window.clear()
        for cx, cy, color in self.rects:
            x = cx * self.pixels_per_unit
            y = cy * self.pixels_per_unit
            rect = pyglet.shapes.Rectangle(x, y, self.pixels_per_unit, self.pixels_per_unit, color=color)
            rect.anchor_position = 0, 0
            rect.draw()
