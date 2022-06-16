from abc import ABC, abstractmethod
from enum import Enum

from src.SceneElements.elements import BaseSceneElement


class ComponentType(Enum):
    ROW = 'row'
    COL = 'col'
    VIEWER = 'viewer'
    SCENE_SETTINGS = 'general_settings'
    ELEMENT_TREE = 'element_tree'
    UNKNOWN = 'unknown'


class BaseComponent(ABC):
    key_component_id = 'componentId'
    key_data = 'data'
    key_children = 'children'
    key_component = 'component'

    def __init__(self) -> None:
        super().__init__()
        self.component_id = -1
        self.children = []
        self.data = {}
        self.component = ComponentType.COL

    def add_child(self, child):
        self.children.append(child)

    @abstractmethod
    def to_json(self, component_id: int) -> dict:
        pass


class Row(BaseComponent):

    def __init__(self) -> None:
        super().__init__()
        self.component = ComponentType.ROW

    def to_json(self, component_id: int) -> dict:
        self.component_id = component_id

        children_json = []
        i = 0
        for child in self.children:
            children_json.append(child.to_json(i))
            i += 1

        return {
            self.key_component: self.component.value,
            self.key_component_id: self.component_id,
            self.key_data: self.data,
            self.key_children: children_json
        }


class Col(BaseComponent):
    key_width = 'width'
    component = ComponentType.COL

    def __int__(self) -> None:
        super().__init__()

    def set_width(self, width: int):
        self.data[self.key_width] = width

    def to_json(self, component_id: int) -> dict:
        self.component_id = component_id

        children_json = []
        i = 0
        for child in self.children:
            children_json.append(child.to_json(i))
            i += 1
        print(self.component.value)
        return {
            self.key_component: self.component.value,
            self.key_component_id: self.component_id,
            self.key_data: self.data,
            self.key_children: children_json
        }


class Group:

    def __init__(self, name: str) -> None:
        super().__init__()
        self.group_id = -1
        self.name = name
        self.ids = []
        self.groups = []
        self.visible = True

    def add_id(self, component_id: int):
        self.ids.append(component_id)

    def add_group(self, group):
        self.groups.append(group)

    def to_json(self, group_id: int) -> dict:
        self.group_id = group_id
        print('Group parsed: ' + str(group_id))
        return {
            "branchId": self.group_id,
            "name": self.name,
            "ids": self.ids,
            "branches": self.groups,
            "visible": self.visible
        }


class ElementTree(BaseComponent):
    key_groups = 'groups'

    groups = []

    def __init__(self) -> None:
        super().__init__()
        self.groups = []
        self.component = ComponentType.ELEMENT_TREE

    def add_group(self, group: Group):
        self.groups.append(group)

    def to_json(self, component_id: int) -> dict:
        self.component_id = component_id

        group_json = []
        i = 0
        for group in self.groups:
            group_json.append(group.to_json(i))
            i += 1
        self.data[self.key_groups] = group_json

        return {
            self.key_component_id: self.component_id,
            self.key_component: self.component.value,
            self.key_data: self.data,
            self.key_children: [],  # no children after Element Tree
        }


class SceneSettings(BaseComponent):
    scene_id = 'sceneId'

    def __init__(self) -> None:
        super().__init__()
        self.component = ComponentType.SCENE_SETTINGS

    def set_scene_id(self, scene_id):
        self.data[self.scene_id] = scene_id

    def to_json(self, component_id: int) -> dict:
        self.component_id = component_id

        return {
            self.key_component: self.component.value,
            self.key_component_id: self.component_id,
            self.key_data: self.data,
            self.key_children: [],  # no children after Scene Settings
        }


class Camera:
    position = []
    rotation = []
    fov = 60
    near = 0.1
    far = 100000
    last_update = 0

    def __init__(self) -> None:
        super().__init__()

    def to_json(self) -> dict:

        return {
            'position': self.position,
            'rotation': self.rotation,
            'fov': self.fov,
            'near': self.near,
            'far': self.far,
            'lastUpdate': self.last_update
        }


class Viewer(BaseComponent):
    key_scene_id = 'sceneId'
    key_camera = 'camera'
    key_elements = 'elements'

    def __init__(self) -> None:
        super().__init__()
        self.data[self.key_elements] = []
        self.data[self.key_scene_id] = 0  # default scene_id
        self.component = ComponentType.VIEWER
        self.camera = Camera()
        self.elements = []

    def add_element(self, element: BaseSceneElement):
        self.elements.append(element)

    def set_camera(self, camera: Camera):
        self.camera = camera

    def set_scene_id(self, scene_id):
        self.data[self.key_scene_id] = scene_id

    def to_json(self, component_id: int) -> dict:
        self.data[self.key_camera] = self.camera.to_json()

        element_json = []
        i = 0
        for elem in self.elements:
            element_json.append(elem.to_json(i))
            i += 1
        self.data[self.key_elements] = element_json

        return {
            self.key_component: self.component.value,
            self.key_component_id: component_id,
            self.key_data: self.data,
            self.key_children: []  # no children allowed after ViewerComponent
        }
