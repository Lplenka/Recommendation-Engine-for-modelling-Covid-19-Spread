import pyglet
from enum import Enum
from typing import List, Tuple

from store import Store
from store_path import StorePath

TupleInt = Tuple[int, int]


class TileType(Enum):
    EMPTY = 0
    WALL = 1
    SHELF = 2
    ENTRANCE = 3
    EXIT = 4


class Visualizer:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    DGREY = (100, 100, 100)
    LGREY = (180, 180, 180)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    def __init__(self, config: dict, store: Store) -> None:
        """Visualizes the store and customer paths using pyglet"""
        # read config values
        self.ppu = config['visualizer']['pixels_per_unit']
        self.store = store
        # calc some other values
        self.unit_width = 2 + (self.store.n_aisles_w * 3)
        self.unit_height = 3 + (self.store.n_aisles_h * (self.store.n_shelves + 1))
        self.width = self.ppu * self.unit_width
        self.height = self.ppu * self.unit_height
        # setup pyglet window
        self.window = pyglet.window.Window()
        self.on_draw = self.window.event(self.on_draw)
        self.window.set_size(self.width, self.height)
        # setup batches, groups and graphics
        self.batch = pyglet.graphics.Batch()
        self.group_bg = pyglet.graphics.OrderedGroup(0)
        self.group_fg0 = pyglet.graphics.OrderedGroup(1)
        self.group_fg1 = pyglet.graphics.OrderedGroup(2)
        self.graphics = []
        self.__generate_store_graphics()
    
    def run(self) -> None:
        """Start pyglet"""
        pyglet.gl.glClearColor(*self.__color_convert(self.WHITE))
        pyglet.app.run()
    
    def on_draw(self) -> None:
        """Draw the window"""
        self.window.clear()
        for graphic in self.graphics:
            graphic.draw()

    def add_path(self, path: StorePath) -> None:
        """Adds a customer's path to the visualiser"""
        self.__generate_path_graphics(path)

    def __generate_store_graphics(self) -> None:
        """Generates graphics which draw the store layout"""
        tile_colors = {
            TileType.ENTRANCE: self.GREEN,
            TileType.EXIT: self.RED,
            TileType.SHELF: self.DGREY,
            TileType.WALL: self.BLACK
        }
        for x in range(self.unit_width):
            for y in range(self.unit_height):
                tile_type = self.__get_tile_type(x, y)
                if tile_type != TileType.EMPTY:
                    rect = pyglet.shapes.Rectangle(
                        x * self.ppu, y * self.ppu, self.ppu, self.ppu, color=tile_colors[tile_type],
                        batch=self.batch, group=self.group_bg
                    )
                    rect.anchor_position = 0, 0
                    self.graphics.append(rect)
    
    def __generate_path_graphics(self, path: StorePath) -> None:
        """Generates graphics which draw the given path"""
        # generate lines for the paths between nodes
        for i in range(len(path.nodes_path) - 1):
            x0, y0 = self.__coord_to_center(*self.__node_to_coord(path.nodes_path[i]))
            x1, y1 = self.__coord_to_center(*self.__node_to_coord(path.nodes_path[i + 1]))
            line = pyglet.shapes.Line(
                x0, y0, x1, y1, width=5, color=self.LGREY,
                batch=self.batch, group=self.group_fg0
            )
            line.opacity = 150
            self.graphics.append(line)
        # generate circular nodes
        for node in path.nodes_visit:
            x, y = self.__coord_to_center(*self.__node_to_coord(node))
            circ = pyglet.shapes.Circle(
                x, y, self.ppu * 0.25, color=self.BLUE,
                batch=self.batch, group=self.group_fg1
            )
            self.graphics.append(circ)

    def __get_tile_type(self, x: int, y: int) -> TileType:
        """Gets the type of tile at the given (x, y) coordinate"""
        if self.__is_entrance_tile(x, y):
            return TileType.ENTRANCE
        elif self.__is_exit_tile(x, y):
            return TileType.EXIT
        elif self.__is_wall_tile(x, y):
            return TileType.WALL
        elif self.__is_shelf_tile(x, y):
            return TileType.SHELF
        return TileType.EMPTY

    def __is_entrance_tile(self, x: int, y: int) -> bool:
        """Checks if an entrance is at the given (x, y) coordinate"""
        return x == 2 and y == 0
    
    def __is_exit_tile(self, x: int, y: int) -> bool:
        """Checks if an exit is at the given (x, y) coordinate"""
        return x == self.unit_width - 3 and y == 0
    
    def __is_shelf_tile(self, x: int, y: int) -> bool:
        """Checks if a shelf is at the given (x, y) coordinate"""
        return self.__is_shelf_tile_x(x) and self.__is_shelf_tile_y(y)
    
    def __is_wall_tile(self, x: int, y: int) -> bool:
        """Checks if a wall is at the given (x, y) coordinate"""
        if x == 0 or x == self.unit_width - 1 or y == 0 or y == self.unit_height - 1:
            return True
        if not self.__is_shelf_tile_y(y) and (x == 1 or x == self.unit_width - 2):
            return True
        return False

    def __is_shelf_tile_x(self, x: int) -> bool:
        """Checks if a shelf could be at the given x coordinate"""
        return (x - 2) % 3 != 0
    
    def __is_shelf_tile_y(self, y: int) -> bool:
        """Checks if a shelf could be at the given y coordinate"""
        return (y - 1) % (self.store.n_shelves + 1) != 0

    def __color_convert(self, color: List[int]) -> List[float]:
        """Maps a color's channels to (0,1) and adds an alpha channel"""
        return [c / 255 for c in color] + [0]

    def __node_to_coord(self, node: int) -> TupleInt:
        """Gets the (x, y) coordinates for a given node"""
        if node == self.store.node_start:
            return (2, 0)
        elif node == self.store.node_end:
            return (self.unit_width - 3, 0)
        x = 2 + ((node // self.store.n_nodes_h) * 3)
        y = 1 + (node % self.store.n_nodes_h)
        return (x, y)
    
    def __coord_to_center(self, x: int, y: int) -> TupleInt:
        """Gets the center of a unit's coordinates"""
        x = (x * self.ppu) + (self.ppu / 2)
        y = (y * self.ppu) + (self.ppu / 2)
        return (x, y)
