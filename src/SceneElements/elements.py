from abc import ABC, abstractmethod
from enum import Enum


class BaseSceneElement(ABC):
    name = 'name'
    transformation = 'transformation'

    def __init__(self) -> None:
        super().__init__()

    attributes = {}

    def add_name(self, name: str):
        self.attributes[self.name] = name

    def add_transformation(self, transformation):
        self.attributes[self.transformation] = transformation

    @abstractmethod
    def add_source(self, source):
        pass


class PointCloudType(Enum):
    POTREE = 'potree_point_cloud'
    DEFAULT = 'default_point_cloud'


class PointCloud(BaseSceneElement):

    def __init__(self, point_cloud_type=PointCloudType.POTREE) -> None:
        super().__init__()
        self.point_cloud_type = point_cloud_type
        self.source = ''

    def add_source(self, url: str):
        self.source = url


class LineSet(BaseSceneElement):

    def __init__(self) -> None:
        super().__init__()
        self.source = []

    def add_source(self, line: [(int, int)]):
        self.source.append(line)


class CameraTrajectory(BaseSceneElement):

    translation = 't'
    rotation = 'r'
    image_url = 'imageUrl'

    def __init__(self) -> None:
        super().__init__()
        self.source = {}

    def add_source(self, source: ([int], [int])):
        self.source[self.translation] = source[0]
        self.source[self.rotation] = source[1]

    def add_image(self, url: str):
        self.attributes[self.image_url] = url
