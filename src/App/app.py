from flask_socketio import SocketIO, emit
from flask import Flask
import flask
import json
import secrets

from src.Components.base import Row, Viewer, Camera, ElementTree, Col, SceneSettings, Group
from src.SceneElements.elements import PotreePointCloud, DefaultPointCloud, LineSet, CameraTrajectory, BaseSceneElement


# Allow all accesses by default.
def set_cors_headers(response: flask.Response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


class Tarasp:
    app = Flask(__name__)
    socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins='*')

    COMPONENT_TREE = []
    CURRENT_CAMERA_STATE = {}

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

        pc3 = DefaultPointCloud(name="Fragment")
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
        else:
            # TODO throw error?
            print("[Error]: Type of element unknown")

    def add_point_cloud(self, pc, name='Default PointCloud'):
        if isinstance(pc, DefaultPointCloud):
            self._POINT_CLOUDS.append(pc)
        elif isinstance(pc, str):
            point_cloud = DefaultPointCloud(name=name)
            point_cloud.set_source(pc)
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

    def add_group(self, group):
        self._GROUPS.append(group)

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

            for ppc in self._POTREE_POINT_CLOUDS:
                viewer.add_element(ppc)

            for ls in self._LINE_SETS:
                viewer.add_element(ls)

            for ct in self._CAMERA_TRAJECTORIES:
                viewer.add_element(ct)

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
    @app.route('/component_tree/<path:tree_id>')
    def get_component_tree(tree_id):
        tree_id = int(tree_id)
        if len(Tarasp.COMPONENT_TREE) < tree_id:
            response = flask.make_response("[Server]: Error: No component tree found with the provided ID")
            response.status_code = 404
            return set_cors_headers(response)
        else:
            response = flask.make_response(flask.jsonify(Tarasp.COMPONENT_TREE[tree_id]))
            response.status_code = 200
            return set_cors_headers(response)

    # SocketIO

    @staticmethod
    @socketio.on('json')
    def test_message(message):
        data = json.loads(message)
        scene_id = data['sceneId']
        state = data['state']
        if len(Tarasp.CURRENT_CAMERA_STATE) == 0:
            Tarasp.CURRENT_CAMERA_STATE[scene_id] = state
        else:
            last_update = Tarasp.CURRENT_CAMERA_STATE[scene_id]['lastUpdate']

            if last_update + 30 < state['lastUpdate']:
                Tarasp.CURRENT_CAMERA_STATE[scene_id] = state
                emit('json', state, broadcast=True, include_self=False)

    @staticmethod
    @socketio.on('connect')
    def test_connect():
        print('Client connected')

    @staticmethod
    @socketio.on('disconnect')
    def test_disconnect():
        print('Client disconnected')
