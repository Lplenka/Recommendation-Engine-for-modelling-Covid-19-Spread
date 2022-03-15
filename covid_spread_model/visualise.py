import pyglet


class Visualiser:
    COLOR_BLACK = (0, 0, 0)
    COLOR_DARKGREY = (100, 100, 100)
    COLOR_LIGHTGREY = (180, 180, 180)
    COLOR_RED = (255, 0, 0)
    COLOR_GREEN = (0, 255, 0)
    COLOR_BLUE = (0, 0, 255)

    def __init__(self, config, graph, path):
        self.config = config
        self.graph = graph
        self.path = path
        self.window = pyglet.window.Window()
        self.on_draw = self.window.event(self.on_draw)
        # config stuff
        self.num_aisles_hor = self.config['num_aisles_horizontal']
        self.num_aisles_ver = self.config['num_aisles_vertical']
        self.num_shelves = self.config['num_shelves_per_aisle']
        # widths, heights
        self.unit_width = 2 + (self.num_aisles_hor * 3)
        self.unit_height = 3 + (self.num_aisles_ver * (self.num_shelves + 1))
        self.pixels_per_unit = 50
        self.width = self.pixels_per_unit * self.unit_width
        self.height = self.pixels_per_unit * self.unit_height
        self.window.set_size(self.width, self.height)
        # draw store
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
        # draw nodes and path
        self.num_nodes_hor = self.num_aisles_hor
        self.num_nodes_ver = 1 + (self.num_aisles_ver * (self.num_shelves + 1))
        self.num_nodes = 2 + (self.num_nodes_hor * self.num_nodes_ver)
        self.start_node = self.num_nodes - 2
        self.end_node = self.num_nodes - 1
        self.circles = []
        for node in self.path['nodes']:
            self.circles.append(self.node_to_coords(node))
        self.lines = []
        for i in range(len(self.path['path']) - 1):
            self.lines.append((
                self.node_to_coords(self.path['path'][i]),
                self.node_to_coords(self.path['path'][i + 1]),
            ))
        print(self.config['seed'])
    
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
        return (y - 1) % (self.num_shelves + 1) != 0

    def is_start_door(self, x, y):
        return x == 2 and y == 0
    
    def is_end_door(self, x, y):
        return x == self.unit_width - 3 and y == 0

    def node_to_coords(self, node):
        if node == self.start_node:
            return (2, 0)
        elif node == self.end_node:
            return (self.unit_width - 3, 0)
        x = 2 + ((node // self.num_nodes_ver) * 3)
        y = 1 + (node % self.num_nodes_ver)
        return (x, y)

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
        for (cx1, cy1), (cx2, cy2) in self.lines:
            x1 = (cx1 * self.pixels_per_unit) + (self.pixels_per_unit / 2)
            y1 = (cy1 * self.pixels_per_unit) + (self.pixels_per_unit / 2)
            x2 = (cx2 * self.pixels_per_unit) + (self.pixels_per_unit / 2)
            y2 = (cy2 * self.pixels_per_unit) + (self.pixels_per_unit / 2)
            line = pyglet.shapes.Line(x1, y1, x2, y2, width=5, color=self.COLOR_LIGHTGREY)
            line.opacity = 150
            line.draw()
        for cx, cy in self.circles:
            x = (cx * self.pixels_per_unit) + (self.pixels_per_unit / 2)
            y = (cy * self.pixels_per_unit) + (self.pixels_per_unit / 2)
            circ = pyglet.shapes.Circle(x, y, self.pixels_per_unit * 0.25, color=self.COLOR_BLUE)
            circ.draw()
        for i in range(self.num_nodes):
            cx, cy = self.node_to_coords(i)
            x = (cx * self.pixels_per_unit) + (self.pixels_per_unit / 2)
            y = (cy * self.pixels_per_unit) + (self.pixels_per_unit / 2)
