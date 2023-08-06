class ChildComponentNotExistsException(Exception):
    def __init__(self, component:str) -> None:
        self.component = component

    def __str__(self) -> str:
        return f"{self.component} not present as child component"
