import pygame
import moderngl

class Texture:
    def __init__(self, ctx) -> None:
        self.ctx = ctx
        self.textures = {}
        self.textures[0] = self.get_texture(path='./textures/test.png')
        self.textures[1] = self.get_texture(path='./textures/img1.png')
        self.textures[2] = self.get_texture(path='./textures/img2.png')
        self.textures[3] = self.get_texture(path='./textures/img3.png')


    def get_texture(self, path):
        texture = pygame.image.load(path).convert()
        texture = pygame.transform.flip(texture, flip_x=False, flip_y=True)
        texture = self.ctx.texture(size=texture.get_size(),
                                   components = 3,
                                   data = pygame.image.tostring(texture, 'RGB'))
        
        texture.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        texture.build_mipmaps()
        
        return texture
    
    def destroy(self):
        [tex.release for tex in self.textures.values()]
