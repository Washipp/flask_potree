import os
import subprocess
from abc import ABC, abstractmethod
from enum import Enum
from os.path import exists
from sys import platform
from typing import Union, List
from pathlib import Path

import pycolmap

from src.colmap_manager import pcd_from_colmap, write_pointcloud_o3d


def ply_to_potree(ply_location: str, overwrite=False) -> str:
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

    BASE_URL = 'http://127.0.0.1'
    PORT = 5000

    _increment: Incrementer = Incrementer()

    def __init__(self, name: str, group: Union[str, List[str]] = "Default") -> None:
        super().__init__()
        self.attributes = {}
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

    def __init__(self, data, name: str = "PotreePointCloud",
                 group: Union[str, List[str]] = "Potree Point Clouds") -> None:
        super().__init__(name, group)
        self.source = ''
        self.data = data
        self.type = SceneElementType.POTREE_PC
        self.material = {self.key_size: 2}
        self.attributes[self.key_material] = self.material

    def set_source(self, url: str):
        self.source = url

    def convert_to_source(self):
        # TODO What other type of data to support? Library?
        # 1. Bring 'data' into .ply form

        if type(self.data) is str and exists(self.data):
            url = self.data
        else:
            self.set_source(self.data)
            url = ''
            return  # return as default since it fails
        # 2. Check if this point-cloud has been transformed before
        # url = './data/fragment.ply'
        # 3. Start new thread to convert it into Potree format if its new
        path = f"{self.BASE_URL}:{str(self.PORT)}{ply_to_potree(url)[1:]}/"
        # 4. Add data-path to source
        path = 'http://127.0.0.1:5000/data/mesh_simplified_converted/'
        self.set_source(path)

    def to_json(self):
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: self.element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }


class DefaultPointCloud(BaseSceneElement):

    def __init__(self, data, name="Point Cloud", group: Union[str, List[str]] = "Default Point Clouds") -> None:
        super().__init__(name, group)
        self.source = ''
        self.data = data
        self.type = SceneElementType.DEFAULT_PC

    def set_source(self, url: str):
        self.source = url

    def convert_to_source(self):
        # TODO
        # 1. Bring 'data' into .ply form
        # 2. Save pc or if this point-cloud has been saved before read url
        # 3. Add data-path to source
        self.set_source('path/to/source/default_pc')

    def to_json(self):
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: self.element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }


class LineSet(BaseSceneElement):

    def __init__(self, name="Line Set", group: Union[str, List[str]] = "Line Sets") -> None:
        super().__init__(name, group)
        self.source = []
        self.type = SceneElementType.LINE_SET

    def set_source(self, lines: []):
        self.source = lines

    def convert_to_source(self):
        # TODO
        # 1. Bring 'data' into 'Array of int-tuple arrays' form
        # 2. Call add source
        self.set_source([[(-10, -5, 0), (-10, 5, 0)]])

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

    def __init__(self, image_url: Union[Path, str], name: str = "Camera Trajectory",
                 group: Union[str, List[str]] = "Default") -> None:
        super().__init__(name, group)
        self.source = {}
        if type(image_url) is str:
            image_url = Path(image_url)
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
        # 2. Call set source
        self.set_source(([5, 5, 5], [2, 2, 2, 0]))

    def to_json(self):
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: self.element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }


class ColmapReconstruction(BaseSceneElement):
    DEFAULT_PATH = './data/colmap/'

    def __init__(self, path: Path, name: str = "Colmap Reconstruction",
                 group: Union[str, List[str]] = "Default",
                 point_cloud_type: PointCloudType = PointCloudType.POTREE) -> None:
        super().__init__(name, group)

        # create internal objects.
        rec = pycolmap.Reconstruction(path)

        # point cloud
        pcd = pcd_from_colmap(rec)
        saved_path = Path(f"{self.DEFAULT_PATH}/{path.name}")
        write_pointcloud_o3d(saved_path, pcd)
        if point_cloud_type == PointCloudType.POTREE:
            self.pc = PotreePointCloud(saved_path, name, group)
        else:
            self.pc = DefaultPointCloud(saved_path, name, group)

        # camera frustums

    def set_source(self, source):
        pass

    def convert_to_source(self):
        pass

    def to_json(self):
        pass
