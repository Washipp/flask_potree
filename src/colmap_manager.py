import open3d as o3d
import numpy as np
from copy import deepcopy

from pathlib import Path
import plyfile

from pycolmap import Reconstruction


def pcd_from_colmap(rec, min_track_length=4, max_reprojection_error=8):
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
        print(camera)
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
        print(np.asarray(cam.points))
        print("---")
        # cameras[camera_name] = Camera(camera_name, cam, image)


# Copied from https://github.com/cvg/pcdmeshing/blob/main/pcdmeshing/utils.py#L108-L138


def write_pointcloud_o3d(path: Path, pcd: o3d.geometry.PointCloud,
                         write_normals: bool = True, xyz_dtype: str = 'float32') -> Path:
    """Currently o3d.t.io.write_point_cloud writes non-standard types but #4553 should fixe it."""
    write_normals = write_normals and pcd.has_normals()
    dtypes = [('x', xyz_dtype), ('y', xyz_dtype), ('z', xyz_dtype)]
    if write_normals:
        dtypes.extend([('nx', xyz_dtype), ('ny', xyz_dtype), ('nz', xyz_dtype)])
    if pcd.has_colors():
        dtypes.extend([('red', 'u1'), ('green', 'u1'), ('blue', 'u1')])
    data = np.empty(len(pcd.points), dtype=dtypes)
    data['x'], data['y'], data['z'] = np.asarray(pcd.points).T
    if write_normals:
        data['nx'], data['ny'], data['nz'] = np.asarray(pcd.normals).T
    if pcd.has_colors():
        colors = (np.asarray(pcd.colors)*255).astype(np.uint8)
        data['red'], data['green'], data['blue'] = colors.T
    with open(str(path), mode='w+b') as f:
        plyfile.PlyData([plyfile.PlyElement.describe(data, 'vertex')]).write(f)
    return path


def write_pointcloud_np(path: Path, points: np.ndarray):
    """Only writes the point coordinates but preserves the float32 dtype."""
    o3d.t.io.write_point_cloud(
        str(path),
        o3d.t.geometry.PointCloud(o3d.core.Tensor(points)))
