import open3d as o3d
import numpy as np
from copy import deepcopy

from pycolmap import Reconstruction


def _pcd_from_colmap(rec, min_track_length=4, max_reprojection_error=8):
    points = []
    colors = []
    for p3D in rec.points3D.values():
        if p3D.track.length() < min_track_length:
            continue
        if p3D.error > max_reprojection_error:
            continue
        points.append(p3D.xyz)
        colors.append(p3D.color / 255.)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np.stack(points))
    pcd.colors = o3d.utility.Vector3dVector(np.stack(colors))
    return pcd


def construct_cameras(rec: Reconstruction, name: str, scale: float):
    camera_lines = {}
    for camera in rec.cameras.values():
        camera_lines[camera.camera_id] = o3d.geometry.LineSet.create_camera_visualization(
            camera.width, camera.height, camera.calibration_matrix(), np.eye(4), scale=scale)
    #
    #     print((camera_lines[camera.camera_id]))
    # print(camera_lines)

    cameras = {}
    # Draw the frustum for each image
    for image in rec.images.values():
        T = np.eye(4)
        T[:3, :4] = image.inverse_projection_matrix()
        cam = deepcopy(camera_lines[image.camera_id]).transform(T)
        cam.paint_uniform_color([1.0, 0.0, 0.0])  # red
        camera_name = name + "-" + image.name
        print(cam.points)
        # cameras[camera_name] = Camera(camera_name, cam, image)

