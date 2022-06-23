from src.App.app import Tarasp
from src.Components.base import Camera
from src.SceneElements.elements import PotreePointCloud

path = './data/colmap/demo/sfm'

app = Tarasp(print_component_tree=True)

app.add_element(PotreePointCloud(data='../data/mesh.ply', name="Fragment", group="Group 1"))

animation_name = "animation_1"

for i in range(50):
    cam = Camera([100, 100 + i / 2, 100 + i], [0.5, 0.5, 0.5, 2, 0.5])
    app.add_animation(animation_name, cam)

app.run()
