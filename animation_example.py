from src.App.app import Tarasp
from src.Components.base import CameraState
from src.SceneElements.elements import PotreePointCloud, PointShape

app = Tarasp(print_component_tree=True)

pc = PotreePointCloud(data='../data/mesh.ply')
# pc.set_color('#ff0000')
# pc.set_opacity(0.5)
# pc.set_point_type(PointShape.SQUARED)
app.add_element(pc)


def animation_function(index: int):
    if index > 100:
        return None
    return CameraState([-11.907696868, -33.0262523 - index, 3.9975077 + index / 2],
                       [0.42302607912, -0.06315283658, -0.1015528383, 0.89819133],
                       up=[0.12899716547507342, 0.621471914811951, 0.7727434182180807])


app.add_animation(animation_function,
                  sleep_duration=1,
                  screenshot=True,
                  screenshot_directory='test-directory')

app.run()
