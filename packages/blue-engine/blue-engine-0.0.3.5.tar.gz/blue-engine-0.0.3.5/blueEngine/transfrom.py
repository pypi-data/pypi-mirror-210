import glm
from component import Component

class Transfrom(Component):
    def __init__(self, parent, scale = (1, 1, 1), rotation=(0,0,0), position=(0,0,0)) -> None:
        super().__init__(parent)
        self.scale = glm.vec3(scale)
        self.rotation = glm.vec3(rotation)
        self.position = glm.vec3(position)

    def __str__(self) -> str:
        return f"position = {tuple(self.position)}\nscale = {tuple(self.scale)}\n rotation = {tuple(self.rotation)}"
        
