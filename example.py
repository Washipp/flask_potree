import pycolmap

from src.App.app import Tarasp
from src.Components.base import Group
from src.SceneElements.elements import PotreePointCloud, LineSet, CameraTrajectory
from src.colmap_manager import construct_cameras

app = Tarasp(port=5000)
# app.load_example_elements()

point_cloud = PotreePointCloud(data='./data/fragment.ply', name="ETH-CAB", group="Group 1")
app.add_element(point_cloud)


ls = LineSet(name='Line Set', group=["Group 1", "Group 2", "Group 2", "Group 2"])
app.add_element(ls)

ct = CameraTrajectory(image_url='data/images/')
app.add_element(ct)

# path = './data/colmap/demo/sfm'
#
# try:
#     rec = pycolmap.Reconstruction(path)
#     construct_cameras(rec, 'name', 0.2)
# except Exception as e:
#     print(e)


app.run()
