import numpy as np
import glm

from errors import *
from transfrom import Transfrom

class BaseModel:
    def __init__(self, app, vao_name, tex_id, position=(0, 0, 0), rotation = (0, 0, 0), scale = (1, 1, 1)) -> None:
        self.app = app
        self.components = {'transform':Transfrom(self, scale, rotation, position)}
        self.m_model = self.get_model_matrix()
        self.tex_id = tex_id
        self.vao = app.mesh.vao.vaos[vao_name]
        self.program = self.vao.program
        self.camera = self.app.camera

    def update(self): ...

    def get_model_matrix(self):
        m_model = glm.mat4()
        m_model = glm.translate(m_model, self.components['transform'].position)
        m_model = glm.rotate(m_model, self.components['transform'].rotation.x, glm.vec3(1, 0, 0))
        m_model = glm.rotate(m_model, self.components['transform'].rotation.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.components['transform'].rotation.z, glm.vec3(0, 0, 1))
        m_model = glm.scale(m_model, self.components['transform'].scale)
        return m_model
    
    def render(self):
        self.update()
        self.vao.render()
    def get_component(self, component:str):
        try:
            return self.components[component]
        except KeyError:
            raise ChildComponentNotExistsException(component)

class Cube(BaseModel):
    def __init__(self, app, vao_name='cube', tex_id=0, position = (0, 0, 0), rotation = (0, 0, 0), scale = (1, 1, 1)) -> None:
        super().__init__(app, vao_name, tex_id, position, rotation, scale)
        self.on_init()

    def update(self):
        self.texture.use()
        self.program['m_model'].write(self.m_model)
        self.program['m_view'].write(self.camera.m_view)
        self.program['camPos'].write(self.camera.position)

    def on_init(self):
        self.texture = self.app.mesh.texture.textures[self.tex_id]
        self.program['u_texture_0'] = 0
        self.texture.use()
        
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        
        self.program['light.position'].write(self.app.light.position)
        self.program['light.Ia'].write(self.app.light.Ia)
        self.program['light.Id'].write(self.app.light.Id)
        self.program['light.Is'].write(self.app.light.Is)
