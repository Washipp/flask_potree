import subprocess
from abc import ABC, abstractmethod
from enum import Enum
from os.path import exists

BASE_URL = 'http://127.0.0.1'
PORT = 5000


def ply_to_potree(ply_location: str, overwrite=False) -> str:
    base_converted_directory = './data/converted/'
    base_command = './converter/PotreeConverter'
    name = ply_location.split('/')[-1]

    target = base_converted_directory + name
    full_command = base_command + ' ' + ply_location + ' -o ' + target
    if overwrite:
        subprocess.run(full_command + ' --overwrite', shell=True)
    elif not exists(target + '/cloud.js'):
        subprocess.run(full_command, shell=True)
    else:
        print('PointCloud already found, no conversion needed')

    return target


class BaseSceneElement(ABC):
    key_name = 'name'
    key_transformation = 'transformation'
    key_element_id = 'elementId'
    key_scene_type = 'sceneType'
    key_source = 'source'
    key_attributes = 'attributes'

    def __init__(self) -> None:
        super().__init__()
        self.attributes = {}

    def set_name(self, name: str):
        self.attributes[self.key_name] = name

    def set_transformation(self, transformation):
        self.attributes[self.key_transformation] = transformation

    @abstractmethod
    def set_source(self, source):
        pass

    @abstractmethod
    def convert_to_source(self):
        pass

    @abstractmethod
    def to_json(self, element_id: int):
        pass


class SceneElementType(Enum):
    POTREE_PC = 'potree_point_cloud'
    DEFAULT_PC = 'default_point_cloud'
    CAMERA_TRAJECTORY = 'camera_trajectory'
    LINE_SET = 'line_set'


class PotreePointCloud(BaseSceneElement):

    def __init__(self) -> None:
        super().__init__()
        self.source = ''
        self.type = SceneElementType.POTREE_PC

    def set_source(self, url: str):
        self.source = url

    def convert_to_source(self):
        # TODO
        # 1. Bring 'data' into .ply form
        # 2. Check if this point-cloud has been transformed before
        url = './data/fragment.ply'
        # 3. Start new thread to convert it into Potree format if its new
        path = BASE_URL + ':' + str(PORT) + ply_to_potree(url)[1:] + '/'
        # 4. Add data-path to source
        self.set_source(path)

    def to_json(self, element_id):
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }


class DefaultPointCloud(BaseSceneElement):

    def __init__(self) -> None:
        super().__init__()
        self.source = ''
        self.type = SceneElementType.DEFAULT_PC

    def set_source(self, url: str):
        self.source = url

    def convert_to_source(self):
        # TODO
        # 1. Bring 'data' into .ply form
        # 2. Save pc or if this point-cloud has been saved before read url
        # 3. Add data-path to source
        self.set_source('path/to/source/default_pc')

    def to_json(self, element_id: int):
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }


class LineSet(BaseSceneElement):

    def __init__(self) -> None:
        super().__init__()
        self.source = []
        self.type = SceneElementType.LINE_SET

    def set_source(self, lines: []):
        self.source = lines

    def convert_to_source(self):
        # TODO
        # 1. Bring 'data' into 'Array of int-tuple arrays' form
        # 2. Call add source
        self.set_source([[(-10, -5, 0), (-10, 5, 0)]])

    def to_json(self, element_id):
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }


class CameraTrajectory(BaseSceneElement):
    key_translation = 't'
    key_rotation = 'r'
    key_image_url = 'imageUrl'

    def __init__(self, image_url: str) -> None:
        super().__init__()
        self.source = {}
        self.set_image(image_url)
        self.type = SceneElementType.CAMERA_TRAJECTORY

    def set_source(self, source: ([int], [int])):
        self.source[self.key_translation] = source[0]
        self.source[self.key_rotation] = source[1]

    def set_image(self, url: str):
        self.attributes[self.key_image_url] = url

    def convert_to_source(self):
        # TODO
        # 1. Bring 'data' into translation-vector and rotation-quaternion form
        # 2. Call add source
        self.set_source(([5, 5, 5], [2, 2, 2, 0]))

    def to_json(self, element_id):
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }
