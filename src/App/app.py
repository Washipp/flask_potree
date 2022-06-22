import time
from copy import deepcopy
from typing import Callable, Any, Iterable, Mapping

from flask_socketio import SocketIO, emit
from flask import Flask, copy_current_request_context
import flask
import json
import secrets
import threading

from src.Components.base import Row, Viewer, Camera, ElementTree, Col, SceneSettings, Group
from src.SceneElements.elements import PotreePointCloud, DefaultPointCloud, LineSet, CameraTrajectory, \
    BaseSceneElement, ColmapReconstruction, SceneElementType


# Allow all accesses by default.
def set_cors_headers(response: flask.Response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


class Tarasp:
    app = Flask(__name__)
    socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins='*', async_mode=None)

    COMPONENT_TREE = []

    # TODO: remove this inital state.
    CURRENT_CAMERA_STATE = {
        0:
        {'position': {'x': 90.00531297517658, 'y': 96.62735985109403, 'z': 112.08120700834593},
                            'rotation': {'_x': -0.7114879396027812, '_y': 0.5464364662891037, '_z': 0.42118674763556463,
                                         '_order': 'XYZ'}, 'fov': 60, 'near': 0.1, 'far': 100000,
                            'lastUpdate': 1655898143578}
    }

    BASE_URL = 'http://127.0.0.1'
    PORT = 5000

    _POTREE_POINT_CLOUDS: [PotreePointCloud] = []
    _POINT_CLOUDS: [DefaultPointCloud] = []
    _LINE_SETS: [LineSet] = []
    _CAMERA_TRAJECTORIES: [CameraTrajectory] = []

    _GROUPS: [Group] = []

    def __init__(self, port: int):
        self.PORT = port
        BaseSceneElement.PORT = port
        self.app.config['SECRET_KEY'] = secrets.token_hex(16)

    def run(self):
        # 1. Convert SceneElements to source (url, r/t, array of tuples of int arrays)
        self.convert_scene_elements()

        # 2. Turn object tree into a json-component tree
        self.create_component_tree()

        # 3. Run the application. Open browser by default?
        # print(json.dumps(self.COMPONENT_TREE[0], indent=2))
        self.socketio.run(self.app, port=self.PORT)

    # Adds the scene elements to the default group

    def load_example_elements(self):
        print('Loading example elements.')
        # Elements
        pc1 = PotreePointCloud('', name="ETH-CAB")
        self.add_element(pc1)
        print("Added PotreePointCloud 1")

        pc2 = PotreePointCloud('', name="Lion")
        self.add_element(pc2)
        print("Added PotreePointCloud 2")

        pc3 = DefaultPointCloud('', name="Fragment")
        self.add_element(pc3)
        print("Added Default PC")

        ls = LineSet(name='Line Set')
        self.add_element(ls)
        print("Added LineSet")

        ct = CameraTrajectory(image_url='image/url', name='Camera Trajectory')
        self.add_element(ct)
        print("Added CameraTrajectory")

    def add_element(self, element: BaseSceneElement):
        if isinstance(element, PotreePointCloud):
            self.add_potree_point_cloud(element)
        elif isinstance(element, DefaultPointCloud):
            self.add_point_cloud(element)
        elif isinstance(element, LineSet):
            self.add_line_set(element)
        elif isinstance(element, CameraTrajectory):
            self.add_camera_trajectory(element)
        elif isinstance(element, ColmapReconstruction):
            # TODO add the elements of the reconstruction
            pass
        else:
            raise Exception("Trying to add unknown element: " + str(type(element)))

    def add_point_cloud(self, pc, name='Default PointCloud'):
        if isinstance(pc, DefaultPointCloud):
            self._POINT_CLOUDS.append(pc)
        elif isinstance(pc, str):
            point_cloud = DefaultPointCloud(data=pc, name=name)
            self._POINT_CLOUDS.append(point_cloud)

        # TODO: what other ways could pc be? add them

    def add_potree_point_cloud(self, pc, name='Potree PointCloud'):
        if isinstance(pc, PotreePointCloud):
            self._POTREE_POINT_CLOUDS.append(pc)
        elif isinstance(pc, str):
            point_cloud = PotreePointCloud('', name=name)
            point_cloud.set_source(pc)
            self._POINT_CLOUDS.append(point_cloud)

    def add_line_set(self, line_set):
        self._LINE_SETS.append(line_set)

    def add_camera_trajectory(self, ct):
        self._CAMERA_TRAJECTORIES.append(ct)

    def convert_scene_elements(self):
        for pc in self._POINT_CLOUDS:
            pc.convert_to_source()

        for ppc in self._POTREE_POINT_CLOUDS:
            ppc.convert_to_source()

        for ls in self._LINE_SETS:
            ls.convert_to_source()

        for ct in self._CAMERA_TRAJECTORIES:
            ct.convert_to_source()

    def create_component_tree(self, tree=None):

        if tree is None:  # Create a default tree, left side is a sidebar, right side is the scene
            scene_id = 0

            viewer = Viewer()
            viewer.set_camera(Camera())
            viewer.set_scene_id(scene_id)
            for pc in self._POINT_CLOUDS:
                viewer.add_element(pc)
                self.update_groups(pc)

            for ppc in self._POTREE_POINT_CLOUDS:
                viewer.add_element(ppc)
                self.update_groups(ppc)

            for ls in self._LINE_SETS:
                viewer.add_element(ls)
                self.update_groups(ls)

            for ct in self._CAMERA_TRAJECTORIES:
                viewer.add_element(ct)
                self.update_groups(ct)

            element_tree = ElementTree()
            for group in self._GROUPS:
                element_tree.add_group(group)

            settings = SceneSettings()
            settings.set_scene_id(scene_id)

            side_bar = Col()
            side_bar.set_width(3)
            side_bar.add_child(settings)
            side_bar.add_child(element_tree)

            scene = Col()
            scene.set_width(9)
            scene.add_child(viewer)

            row = Row()
            row.add_child(side_bar)
            row.add_child(scene)

            self.COMPONENT_TREE.append([row.to_json(0)])

        else:
            self.COMPONENT_TREE.append([tree])

    def update_groups(self, element: BaseSceneElement):
        group_names = element.group
        element_id = element.element_id
        selected_group = Group("Unknown")
        current_groups = self._GROUPS
        for name in group_names:
            found = False
            for group in current_groups:
                if group.name == name:  # found, group already exists
                    current_groups = group.groups
                    selected_group = group
                    found = True
                    break
            if not found:
                # group not found, create new object
                selected_group = Group(name)
                current_groups.append(selected_group)
                current_groups = selected_group.groups
        selected_group.add_id(element_id)

    # ----------------------
    # REST-API to get the data
    # ----------------------

    @staticmethod
    @app.route('/')
    def func():
        response = flask.send_from_directory(directory='../../front-end/ts-potree/', path='index.html')
        return set_cors_headers(response)

    @staticmethod
    @app.route('/<path:file_name>')
    def serve_front_end(file_name):
        response = flask.send_from_directory(directory='../../front-end/ts-potree/', path=file_name)
        return set_cors_headers(response)

    # Handle all data calls by returning it as octet-stream.
    @staticmethod
    @app.route('/data/<path:file_name>')
    def serve_data(file_name):
        response = flask.send_from_directory(directory='../../data/', path=file_name, as_attachment=True)
        response.headers.set('Content-Type', 'application/octet-stream')
        return set_cors_headers(response)

    # Get the defined component-tree
    @staticmethod
    @app.route('/component_tree/<path:scene_id>')
    def get_component_tree(scene_id):
        scene_id = int(scene_id)
        if len(Tarasp.COMPONENT_TREE) < scene_id:
            response = flask.make_response("[Server]: Error: No component tree found with the provided ID")
            response.status_code = 404
            return set_cors_headers(response)
        else:
            response = flask.make_response(flask.jsonify(Tarasp.COMPONENT_TREE[scene_id]))
            response.status_code = 200
            return set_cors_headers(response)


    # SocketIO

    ANIMATION = {}

    thread = None
    thread_lock = threading.Lock()

    @staticmethod
    @socketio.on('start_animation')
    def start_animation(scene_id):
        scene_id = int(scene_id)
        print("[Server]: Starting animation for sceneId " + str(scene_id))

        # TODO: replace with actual camera states that correspond to the animation.
        state = deepcopy(Tarasp.CURRENT_CAMERA_STATE[scene_id])

        def send_animation_update():
            count = 1
            for i in range(15):
                state["position"]["x"] -= count
                state["position"]["y"] -= count / 2
                Tarasp.socketio.emit('camera_sync', state, broadcast=False)  # only send to originating user
                Tarasp.socketio.sleep(0.08)
                count += 5
            with Tarasp.thread_lock:
                Tarasp.thread = None

        with Tarasp.thread_lock:
            if Tarasp.thread is None:
                Tarasp.thread = Tarasp.socketio.start_background_task(target=send_animation_update)

    @staticmethod
    @socketio.on('camera_sync')
    def sync_camera_state(message):
        data = json.loads(message)
        scene_id = data['sceneId']
        state = data['state']
        if len(Tarasp.CURRENT_CAMERA_STATE) == 0:
            Tarasp.CURRENT_CAMERA_STATE[scene_id] = state
        else:
            last_update = Tarasp.CURRENT_CAMERA_STATE[scene_id]['lastUpdate']

            if last_update + 30 < state['lastUpdate']:
                Tarasp.CURRENT_CAMERA_STATE[scene_id] = state
                Tarasp.socketio.emit('camera_sync', state, broadcast=True, include_self=False)

    @staticmethod
    @socketio.on('connect')
    def connect():
        print('Client connected')

    @staticmethod
    @socketio.on('disconnect')
    def test_disconnect():
        print('Client disconnected')
