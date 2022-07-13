from abc import ABC, abstractmethod
from enum import Enum
from typing import List

from src.SceneElements.elements import BaseSceneElement, Incrementer


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

        return {
            self.key_component: self.component.value,
            self.key_component_id: self.component_id,
            self.key_data: self.data,
            self.key_children: children_json
        }


class Group:
    key_group_id = 'groupId'
    key_name = 'name'
    key_ids = 'ids'
    key_groups = 'groups'
    key_visible = 'visible'

    _increment: Incrementer = Incrementer()

    def __init__(self, name: str) -> None:
        super().__init__()
        self.group_id = self._get_next_id()
        self.name = name
        self.ids = []
        self.groups = []
        self.visible = True

    def add_id(self, element_id: int) -> None:
        self.ids.append(element_id)

    def add_group(self, group) -> None:
        self.groups.append(group)

    def _get_next_id(self) -> int:
        return self._increment()

    def to_json(self) -> dict:
        group_json = []
        for group in self.groups:
            group_json.append(group.to_json())
        self.groups = group_json

        return {
            self.key_group_id: self.group_id,
            self.key_name: self.name,
            self.key_ids: self.ids,
            self.key_groups: self.groups,
            self.key_visible: self.visible
        }


class ElementTree(BaseComponent):
    key_groups = 'groups'
    key_scene_id = 'sceneId'

    def __init__(self) -> None:
        super().__init__()
        self.groups = []
        self.component = ComponentType.ELEMENT_TREE
        self.data[self.key_scene_id] = 0  # default

    def add_group(self, group: Group):
        self.groups.append(group)

    def set_scene_id(self, scene_id: int):
        self.data[self.key_scene_id] = scene_id

    def to_json(self, component_id: int) -> dict:
        self.component_id = component_id

        group_json = []
        i = 0
        for group in self.groups:
            group_json.append(group.to_json())
            i += 1
        self.data[self.key_groups] = group_json

        return {
            self.key_component_id: self.component_id,
            self.key_component: self.component.value,
            self.key_data: self.data,
            self.key_children: [],  # no children after Element Tree
        }


class SceneSettings(BaseComponent):
    key_scene_id = 'sceneId'

    def __init__(self) -> None:
        super().__init__()
        self.component = ComponentType.SCENE_SETTINGS

    def set_scene_id(self, scene_id):
        self.data[self.key_scene_id] = scene_id

    def to_json(self, component_id: int) -> dict:
        self.component_id = component_id

        return {
            self.key_component: self.component.value,
            self.key_component_id: self.component_id,
            self.key_data: self.data,
            self.key_children: [],  # no children after Scene Settings
        }


class CameraState:
    key_position = 'position'
    key_quaternion = 'quaternion'
    key_up = 'up'
    key_fov = 'fov'
    key_near = 'near'
    key_far = 'far'

    def __init__(self,
                 position: List[float],
                 quaternion: List[float],
                 up=None,
                 fov=60, near=0.1, far=100000) -> None:
        super().__init__()
        if up is None:
            self.up = [0, 1, 0]
        else:
            self.up = up
        self.position = position
        self.quaternion = quaternion
        self.fov = fov
        self.near = near
        self.far = far

    def to_json(self) -> dict:
        return {
            self.key_position: self.position,
            self.key_quaternion: self.quaternion,
            self.key_up: self.up,
            self.key_fov: self.fov,
            self.key_near: self.near,
            self.key_far: self.far,
        }


class Viewer(BaseComponent):
    key_scene_id = 'sceneId'
    key_camera = 'camera'
    key_elements = 'elements'

    def __init__(self, scene_id: int = -1, camera_state=([100, 100, 100], [0.5, 0.5, 0.5, 1])) -> None:
        super().__init__()
        self.data[self.key_elements] = []
        self.data[self.key_scene_id] = scene_id  # default scene_id
        self.component = ComponentType.VIEWER
        self.camera_state = CameraState(camera_state[0], camera_state[1])
        self.elements = []

    def add_element(self, element: BaseSceneElement):
        self.elements.append(element)

    def set_camera(self, camera: CameraState):
        self.camera_state = camera

    def set_scene_id(self, scene_id):
        self.data[self.key_scene_id] = scene_id

    def to_json(self, component_id: int) -> dict:
        self.data[self.key_camera] = self.camera_state.to_json()

        element_json = []
        for elem in self.elements:
            element_json.append(elem.to_json())
        self.data[self.key_elements] = element_json

        return {
            self.key_component: self.component.value,
            self.key_component_id: component_id,
            self.key_data: self.data,
            self.key_children: []  # no children allowed after ViewerComponent
        }
