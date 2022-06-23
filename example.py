from src.App.app import Tarasp
from src.SceneElements.elements import PotreePointCloud, LineSet, CameraTrajectory

app = Tarasp()

ls = LineSet(data=[[(-10, -5, 0), (-10, 5, 0)]], name='Line Set Here', group=["Group 1", "Group 2", "Group 3"])
app.add_element(ls)


ct = CameraTrajectory(data=([2, 2, 2], [2, 2, 2, 2]), image_url='data/images/03903474_1471484089.jpg')
app.add_element(ct)

app.add_element(LineSet(data=[[(-20, -20, 10), (10, 50, 0)]], name='Line Set', group="Group 1"))


point_cloud = PotreePointCloud(data='data/fragment.ply', name="Open3D example", group="Group 1")
app.add_element(point_cloud)

pc = PotreePointCloud(data='../data/mesh.ply', name="ETH-CAB Mesh 8GB", group="Group 1")
app.add_element(pc)


app.run()
