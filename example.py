from src.App.app import Tarasp
from src.SceneElements.elements import PotreePointCloud, LineSet, CameraTrajectory

app = Tarasp(port=5000, print_component_tree=False)

ls = LineSet(data=[[(-10, -5, 0), (-10, 5, 0)]], name=['Dir1', 'Dir2', 'Line Set'])
app.add_element(ls)

app.add_element(LineSet(data=[[(-20, -20, 10), (10, 50, 0)]], name=['Dir1', 'Dir2', 'Line Set 2']))


point_cloud = PotreePointCloud(data='data/fragment.ply', name=['Dir1', 'Open3D example'])
app.add_element(point_cloud)

pc = PotreePointCloud(data='../data/mesh.ply', name="ETH-CAB Mesh 8GB")
app.add_element(pc)


app.run()
