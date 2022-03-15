import pyglet


class Visualiser:
    def __init__(self, config, graph, path):
        self.window = pyglet.window.Window()
    
    def run(self):
        pyglet.gl.glClearColor(1, 1, 1, 0)
        pyglet.app.run()
    
    def on_draw(self):
        self.window.clear()
