import subprocess
from abc import ABC, abstractmethod
from enum import Enum
from os.path import exists
from sys import platform
from typing import Union, List
from pathlib import Path, PosixPath

import open3d as o3d

from src.colmap_manager import write_pointcloud_o3d


def ply_to_potree(ply_location: str, overwrite=False) -> str:
    print("[Info]: Converting point-cloud to potree format.")
    base_converted_directory = './data/converted/'
    # TODO: check the OS and then execute the command.

    name = ply_location.split('/')[-1]
    target = base_converted_directory + name

    full_command = ''

    if platform == "linux":
        # Linux
        base_command = './converter/PotreeConverter'
        full_command = base_command + ' ' + ply_location + ' -o ' + target
    elif platform == "darwin":
        # OS X
        # TODO add support for MacOS and Windows.
        full_command = ''
    elif platform == "win32":
        # Windows...
        full_command = ''

    if overwrite:
        subprocess.run(full_command + ' --overwrite', shell=True)
    elif not exists(target + '/cloud.js'):
        subprocess.run(full_command, shell=True)
    else:
        print('[Info]: PointCloud already found, no conversion needed')

    return target


class Incrementer:
    def __init__(self):
        self.value = -1

    def __call__(self) -> int:
        self.value += 1
        return self.value


class BaseSceneElement(ABC):
    key_name = 'name'
    key_transformation = 'transformation'
    key_element_id = 'elementId'
    key_scene_type = 'sceneType'
    key_source = 'source'
    key_attributes = 'attributes'

    DEFAULT_DATA_PATH = './data/'

    BASE_URL = 'http://127.0.0.1'
    PORT = 5000

    _increment: Incrementer = Incrementer()

    def __init__(self, data, name: str, group: Union[str, List[str]] = "Default") -> None:
        super().__init__()
        self.attributes = {}
        self.data = data
        self.element_id = self._get_next_id()
        self.attributes[self.key_name] = name
        if isinstance(group, str):
            self.group = [group]
        else:
            self.group = group

    def set_transformation(self, transformation):
        self.attributes[self.key_transformation] = transformation

    def _get_next_id(self) -> int:
        return self._increment()

    @abstractmethod
    def set_source(self, source):
        pass

    @abstractmethod
    def convert_to_source(self):
        pass

    @abstractmethod
    def to_json(self):
        pass


class SceneElementType(Enum):
    POTREE_PC = 'potree_point_cloud'
    DEFAULT_PC = 'default_point_cloud'
    CAMERA_TRAJECTORY = 'camera_trajectory'
    LINE_SET = 'line_set'


class PointCloudType(Enum):
    POTREE = 'potree'
    DEFAULT = 'default'


class PotreePointCloud(BaseSceneElement):
    key_material = 'material'
    key_size = 'size'

    def __init__(self, data, name: str = "PotreePointCloud", group: Union[str, List[str]] = "Default") -> None:
        super().__init__(data, name, group)
        self.source = ''
        self.data = data
        self.type = SceneElementType.POTREE_PC

    def set_source(self, url: str):
        self.source = url

    def convert_to_source(self):
        # TODO What other type of data to support? Library?
        # 1. Bring 'data' into .ply form
        if type(self.data) is str:
            if exists(self.data):
                url = self.data
            else:
                raise Exception(f"Data not found {self.data}")
        elif type(self.data) is Path or type(self.data) is PosixPath:
            url = self.data.as_posix()
        else:
            raise Exception(f"Trying to convert {type(self.data)} to str")
        # 2. Check if this point-cloud has been transformed before
        # url = './data/fragment.ply'

        # 3. Start new thread to convert it into Potree format if its new
        out_dir = ply_to_potree(url)
        path = f"{self.BASE_URL}:{str(self.PORT)}{out_dir[1:]}/"

        # 4. Add data-path to source
        # path = 'http://127.0.0.1:5000/data/mesh_simplified_converted/'
        self.set_source(path)

    def to_json(self):
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: self.element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }


class DefaultPointCloud(BaseSceneElement):

    def __init__(self, data, name="Point Cloud", group: Union[str, List[str]] = "Default") -> None:
        super().__init__(data, name, group)
        self.source = ''
        self.data = data
        self.type = SceneElementType.DEFAULT_PC

    def set_source(self, url: str):
        self.source = url

    def convert_to_source(self):
        # TODO
        # 1. Bring 'data' into .ply form
        # 2. Save pc or if this point-cloud has been saved before read url
        if type(self.data) is str:
            if exists(self.data):
                self.set_source(self.data)
            else:
                raise Exception(
                    "Trying to convert data to DefaultPointCloud. Got string but is not a path: " + self.data)
        elif type(self.data) is o3d.geometry.PointCloud:
            saved_path = Path(f"{self.DEFAULT_DATA_PATH}/point-clouds/{self.data.name}")
            write_pointcloud_o3d(saved_path, self.data)
            # TODO paths could depend on the OS. Need to test and verify
            self.set_source(saved_path.as_posix())
        # 3. Add data-path to source

    def to_json(self):
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: self.element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }


class LineSet(BaseSceneElement):

    def __init__(self, data, name="Line Set", group: Union[str, List[str]] = "Default") -> None:
        super().__init__(data, name, group)
        self.source = []
        self.type = SceneElementType.LINE_SET

    def set_source(self, lines: []):
        self.source = lines

    def convert_to_source(self):
        # TODO I'm assuming the data is correct.
        # 1. Bring 'data' into 'Array of int-tuple arrays' form
        # 2. Call add source
        self.set_source(self.data)

    def to_json(self):
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: self.element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }


class CameraTrajectory(BaseSceneElement):
    key_translation = 't'
    key_rotation = 'r'
    key_image_url = 'imageUrl'

    def __init__(self, data, image_url: Union[Path, str], name: str = "Camera Trajectory",
                 group: Union[str, List[str]] = "Default") -> None:
        super().__init__(data, name, group)
        self.source = {}
        if type(image_url) is str:
            image_url = Path(image_url).as_posix()
        self.set_image(f"{self.BASE_URL}:{str(self.PORT)}/{image_url}")
        self.type = SceneElementType.CAMERA_TRAJECTORY

    def set_source(self, source: ([int], [int])):
        self.source[self.key_translation] = source[0]
        self.source[self.key_rotation] = source[1]

    def set_image(self, url: str):
        self.attributes[self.key_image_url] = url

    def convert_to_source(self):
        # TODO
        # 1. Bring 'data' into translation-vector and rotation-quaternion form
        if type(self.data) is tuple:
            if type(self.data[0]) is list:
                self.data = (self.data[0], self.data[1])
            else:
                self.data = (self.data[0].tolist(), self.data[1].tolist())
        # 2. Call set source
        self.set_source(self.data)

    def to_json(self):
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: self.element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }
