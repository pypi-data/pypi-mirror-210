from component import Component

class FontComponent(Component):
    def __init__(self, parent, transform, font_family = 'arial', size = 21, font_color = (0,0,0,0)) -> None:
        super().__init__(parent)
        self.transform = transform
        self.font_family = font_family
        self.size = size
        self.font_color = font_color
