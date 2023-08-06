import pygame
import moderngl
import sys

from mesh import Mesh
from camera import Camera
from light import Light
from model import *
from scene import Scene

class app:
    def __init__(self, size, title, framerate, flags=None, icon_path = 'images/BlueEngineLogo.png') -> None:
        self.size = size
        self.title = title
        self.flags = flags
        self.framerate = framerate
        self.clock = pygame.time.Clock()
        self.scene = None
        self.camera = None
        self.light = None
        self.icon = pygame.image.load(icon_path)
        self.time = 0
        self.delta_time = 0

        self.ctx = None
        
        self.run()

    def run(self):
        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 4)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.set_mode(self.size, flags=pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE)
        pygame.display.set_caption(self.title)
        pygame.display.set_icon(self.icon)
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

        self.ctx=moderngl.create_context()
        self.ctx.enable(flags=moderngl.DEPTH_TEST|moderngl.CULL_FACE)
        
        self.light = Light()
        self.camera = Camera(self)
        self.mesh = Mesh(self)
        self.scene = Scene(self)
  

        self.loop()
        

    def loop(self):
        while True:
            self.get_time()
            pygame.display.set_caption(f'{self.title} @ {int(self.clock.get_fps())} fps')
            self.render()
            self.camera.update()
            self.check_events()
            self.delta_time = self.clock.tick(self.framerate)

    def render(self):
        self.ctx.clear(0.18, 0.20, 0.31)
        self.scene.render()        
        pygame.display.flip()


    def get_time(self):
        self.time = pygame.time.get_ticks()*0.001

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.mesh.destroy()
                pygame.quit()
                sys.exit(0)

if __name__ == "__main__":
    app((800, 450), "title", 60)
