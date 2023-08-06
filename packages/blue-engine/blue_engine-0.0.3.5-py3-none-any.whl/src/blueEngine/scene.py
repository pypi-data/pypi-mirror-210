from model import *
import threading
class Scene:
    def __init__(self, app) -> None:
        self.app = app
        self.objects = []
        self.load()

    def add_object(self, object):
        self.objects.append(object)

    def load(self):
        app = self.app
        add = self.add_object

        n, s = 10 ,2

        for x in range(-n, n, s):
            for z in range(-n, n, s):
                add(Cube(app, tex_id=((x//(z+1))%4), position=(x, -s, z), scale=(1, 1, 1)))

    def render_object(self, obj):
        obj.render()

    def render(self):
        for obj in self.objects:
            # print(obj.components['transform'])
            render_thread = threading.Thread(target=self.render_object, args=(obj,))
            render_thread.run()
