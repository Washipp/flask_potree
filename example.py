import pycolmap

from src.App.app import Tarasp
from src.Components.base import Group
from src.SceneElements.elements import PotreePointCloud, LineSet
from src.colmap_manager import construct_cameras

app = Tarasp(port=5000)
# app.load_example_elements()

# TODO add group name as parameter as an [group1, group2, group3] or string
point_cloud = PotreePointCloud(data='./data/fragment.ply', name="ETH-CAB")
app.add_element(point_cloud)


ls = LineSet(name='Line Set')
app.add_element(ls)

group = Group('Group 1')
group.add_id(point_cloud.element_id)

group1 = Group('Group 2')
group1.add_id(ls.element_id)
group1.visible = False
group.add_group(group1)

app.add_group(group)


path = './data/colmap/demo/sfm'

try:
    rec = pycolmap.Reconstruction(path)
    construct_cameras(rec, 'name', 0.2)
except Exception as e:
    print(e)


# app.run()
