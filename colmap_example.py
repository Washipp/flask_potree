import pycolmap
from pathlib import Path

from src.App.app import Tarasp
from src.SceneElements.elements import PotreePointCloud, CameraTrajectory
from src.colmap_manager import pcd_from_colmap, write_pointcloud_o3d

path = './data/colmap/demo/sfm'

app = Tarasp(print_component_tree=True)

rec = pycolmap.Reconstruction(path)

pcd = pcd_from_colmap(rec)
saved_path = write_pointcloud_o3d(Path("./data/pointclouds/colmap/demo/sfm.ply"), pcd)

cameras = {}
for image in rec.images.values():
    if image.camera_id not in cameras.keys():
        cameras[image.camera_id] = []
    cameras[image.camera_id].append([image.tvec, image.qvec, f"./data/colmap/{image.name}"])

for camera in rec.cameras.values():
    h = (camera.height / 2) / 1000
    w = (camera.width / 2) / 1000
    corners = [[-h, w, 1], [h, w, 1], [h, -w, 1], [-h, -w, 1]]
    app.add_element(CameraTrajectory(corners=corners, cameras=cameras[camera.camera_id], link_images=True))

app.add_element(PotreePointCloud(data=saved_path,
                                 name="Point Cloud Reconstruction",
                                 group="Reconstruction"))

app.run()
