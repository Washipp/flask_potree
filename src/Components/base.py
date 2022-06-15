from abc import ABC


class BaseComponent(ABC):

    def __init__(self) -> None:
        super().__init__()

    children = []
    data = {}

    def add_child(self, child):
        self.children.append(child)


class Row(BaseComponent):

    def __init__(self) -> None:
        super().__init__()


class Col(BaseComponent):

    width = 'width'

    def __int__(self, width: int) -> None:
        super().__init__()
        self.data[width] = width


class Group:

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.ids = []
        self.groups = []

    def add_id(self, component_id: int):
        self.ids.append(component_id)

    def add_group(self, group):
        self.groups.append(group)


class ElementTree(BaseComponent):

    groups = 'groups'

    def __init__(self) -> None:
        super().__init__()
        self.data[self.groups] = []

    def add_group(self, group: Group):
        self.data[self.groups].append(group)


class SceneSettings(BaseComponent):

    scene_id = 'sceneId'

    def __init__(self) -> None:
        super().__init__()

    def add_scene_id(self, scene_id):
        self.data[self.scene_id] = scene_id


class Viewer(BaseComponent):

    scene_id = 'sceneId'
    camera = 'camera'
    elements = 'elements'

    def __init__(self) -> None:
        super().__init__()
        self.data[self.elements] = []

    def add_element(self, element):
        self.data[self.elements].append(element)

    def add_camera(self, camera):
        self.data[self.camera] = camera

    def add_scene_id(self, scene_id):
        self.data[self.scene_id] = scene_id
