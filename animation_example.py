from src.App.app import Tarasp
from src.Components.base import CameraState
from src.SceneElements.elements import PotreePointCloud

app = Tarasp(print_component_tree=True)

app.add_element(PotreePointCloud(data='../data/mesh.ply'))


def animation_function(index: int) -> CameraState:
    return CameraState([50, 50 + (index % 50), 50 + (index % 50)], [0.5, 0.5, 0.5, 2, 0.5])


app.add_animation("animation_1", animation_function)

app.run()
