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
    if index > 50:
        return None
    return CameraState([50, 50 + (index % 50), 50 + (index % 50)], [0.5, 0.5, 0.5, 0.5])


app.add_animation("animation_1",
                  animation_function,
                  sleep_duration=0.5,
                  screenshot=True,
                  screenshot_directory='test-directory')

app.run()
