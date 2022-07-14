import hashlib
import subprocess
from abc import ABC, abstractmethod
from enum import Enum
from os.path import exists
from sys import platform
from typing import Union, List
from pathlib import Path, PosixPath

import numpy
import open3d as o3d

from src.colmap_manager import write_pointcloud_o3d


def ply_to_potree(ply_location: str, overwrite=False) -> str:
    print("[Info]: Converting point-cloud to potree format.")
    base_converted_directory = './data/converted/'

    if not exists(base_converted_directory):
        Path(base_converted_directory).mkdir(parents=True)
    # TODO: check the OS and then execute the command.

    name = str(int(hashlib.md5(ply_location.encode()).hexdigest(), 16))
    print(f"[Info]: Hash of path '{ply_location}' is '{name}'")
    target = base_converted_directory + name

    full_command = ''

    if platform == "linux":
        # Linux
        base_command = './converter/PotreeConverter'
        full_command = f"{base_command} {ply_location} -o {target}"
    elif platform == "darwin":
        # OS X...
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
    key_material = 'material'

    DEFAULT_DATA_PATH = './data/'

    BASE_URL = 'http://127.0.0.1'
    PORT = 5000

    _increment: Incrementer = Incrementer()

    def __init__(self, data, name: Union[str, List[str]], transformation: numpy.ndarray = None) -> None:
        super().__init__()
        self.attributes = {}
        self.data = data
        self.element_id = self._get_next_id()
        if isinstance(name, str):
            self.name = [name]
        else:
            self.name = name
        self.attributes[self.key_name] = '/'.join(self.name)
        if transformation is not None:
            self.set_transformation(transformation)
        self.material = {}

    def set_transformation(self, transformation: numpy.ndarray):
        self.attributes[self.key_transformation] = numpy.concatenate(transformation).tolist()

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


class PointShape(Enum):
    CIRCLE = 'CIRCLE'
    SQUARED = 'SQUARE'


class PotreePointCloud(BaseSceneElement):
    key_color = 'color'
    key_point_size = 'pointSize'
    key_point_type = 'pointType'
    key_opacity = 'opacity'

    def __init__(self,
                 data,
                 color: str = None,
                 point_size: float = None,
                 point_type: PointShape = None,
                 opacity: float = None,
                 name: Union[str, List[str]] = "Default",
                 transformation: numpy.ndarray = None) -> None:
        super().__init__(data, name, transformation)
        self.source = ''
        self.data = data
        self.type = SceneElementType.POTREE_PC
        if color is not None:
            self.set_color(color)
        if point_size is not None:
            self.set_point_size(point_size)
        if point_type is not None:
            self.set_point_type(point_type)
        if opacity is not None:
            self.set_opacity(opacity)

    def set_source(self, url: str):
        self.source = url

    def set_color(self, color: str):
        self.material[self.key_color] = color

    def set_point_size(self, size: float):
        self.material[self.key_point_size] = size

    def set_point_type(self, point_type: PointShape):
        self.material[self.key_point_type] = point_type.value

    def set_opacity(self, opacity: float):
        self.material[self.key_opacity] = opacity

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
        self.attributes[self.key_material] = self.material
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: self.element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }


class DefaultPointCloud(BaseSceneElement):
    key_material = 'material'
    key_color = 'color'

    def __init__(self, data,
                 name: Union[str, List[str]] = "Default",
                 transformation: numpy.ndarray = None) -> None:
        super().__init__(data, name, transformation)
        self.source = ''
        self.data = data
        self.type = SceneElementType.DEFAULT_PC

    def set_source(self, url: str):
        self.source = url

    def set_color(self, color: str):
        material = {self.key_color: color}
        self.attributes[self.key_material] = material

    def convert_to_source(self):
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

        elif type(self.data) is numpy.asarray:
            # TODO support numpy.arrays
            print("not yet implemented")
        # 3. Add data-path to source

    def to_json(self):
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: self.element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }


class LineSet(BaseSceneElement):

    key_opacity = 'opacity'
    key_color = 'color'
    key_line_width = 'lineWidth'

    def __init__(self,
                 data,
                 opacity: float = None,
                 color: str = None,
                 line_width: float = None,
                 name: Union[str, List[str]] = "Default",
                 transformation: numpy.ndarray = None) -> None:
        super().__init__(data, name, transformation)
        self.source = []
        self.type = SceneElementType.LINE_SET
        if color is not None:
            self.set_color(color)
        if line_width is not None:
            self.set_line_width(line_width)
        if opacity is not None:
            self.set_opacity(opacity)

    def set_source(self, lines: []):
        self.source = lines

    def set_color(self, color: str):
        self.material[self.key_color] = color

    def set_opacity(self, opacity: float):
        self.material[self.key_opacity] = opacity

    def set_line_width(self, width: float):
        self.material[self.key_line_width] = width

    def convert_to_source(self):
        # TODO I'm assuming the data is correct.
        # 1. Bring 'data' into 'Array of int-tuple arrays' form
        # 2. Call add source
        self.set_source(self.data)

    def to_json(self):
        self.attributes[self.key_material] = self.material
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: self.element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }


class CameraTrajectory(BaseSceneElement):
    key_image_url = 'imageUrl'
    key_corners = 'corners'
    key_cameras = 'cameras'
    key_link_images = 'linkImages'

    key_opacity = 'opacity'
    key_color = 'color'
    key_frustum_size = 'frustumSize'
    key_line_width = 'lineWidth'

    def __init__(self,
                 corners: [],
                 cameras: [],
                 link_images: bool = False,
                 opacity: float = None,
                 color: str = None,
                 frustum_size: float = None,
                 line_width: float = None,
                 name: Union[str, List[str]] = "Default",
                 transformation: numpy.ndarray = None) -> None:
        super().__init__(corners, name, transformation)
        self.source = {}
        self.type = SceneElementType.CAMERA_TRAJECTORY
        self.corners = corners
        self.cameras = cameras
        self.link_images = link_images
        if color is not None:
            self.set_color(color)
        if frustum_size is not None:
            self.set_frustum_size(frustum_size)
        if line_width is not None:
            self.set_line_width(line_width)
        if opacity is not None:
            self.set_opacity(opacity)

    def set_source(self, source: {}):
        self.source = source

    def set_color(self, color: str):
        self.material[self.key_color] = color

    def set_frustum_size(self, size: float):
        self.material[self.key_frustum_size] = size

    def set_opacity(self, opacity: float):
        self.material[self.key_opacity] = opacity

    def set_line_width(self, width: float):
        self.material[self.key_line_width] = width

    def set_image(self, url: str):
        self.attributes[self.key_image_url] = url

    def convert_to_source(self):
        # TODO
        # 1. Bring 'corners', 'cameras' and 'link_images' into the correct form

        # replace the image_url to the definite one.
        for c in self.cameras:
            if type(c[0]) is numpy.ndarray:
                c[0] = c[0].tolist()
                c[1] = c[1].tolist()
            image_url = c[2]
            if type(image_url) is str:
                image_url = Path(image_url).as_posix()
            c[2] = f"{self.BASE_URL}:{str(self.PORT)}/{image_url}"

        self.data = {
            self.key_corners: self.corners,
            self.key_link_images: self.link_images,
            self.key_cameras: self.cameras
        }

        # 2. Call set source
        self.set_source(self.data)

    def to_json(self):
        self.attributes[self.key_material] = self.material
        return {
            self.key_scene_type: self.type.value,
            self.key_element_id: self.element_id,
            self.key_source: self.source,
            self.key_attributes: self.attributes
        }
