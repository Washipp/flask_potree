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

for image in rec.images.values():
    app.add_element(CameraTrajectory(data=(image.tvec, image.qvec),
                                     name=image.name,
                                     image_url=f"./data/colmap/{image.name}",
                                     group="Reconstruction"))

app.add_element(PotreePointCloud(data=saved_path,
                                 name="Point Cloud Reconstruction",
                                 group="Reconstruction"))

app.run()
