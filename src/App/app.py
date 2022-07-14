import os
import time
from os.path import exists
from pathlib import Path
from typing import List, Callable, Union
import re

from flask_socketio import SocketIO
from flask import Flask, request
from flask_cors import CORS, cross_origin
import flask
import json
import secrets
import threading

from src.Components.base import Row, Viewer, ElementTree, Col, SceneSettings, Group, CameraState
from src.SceneElements.elements import PotreePointCloud, DefaultPointCloud, LineSet, CameraTrajectory, \
    BaseSceneElement


# Allow all accesses by default. Only works for GET requests, see flask_cors for other requests.
def set_cors_headers(response: flask.Response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


def create_404_response(error: str):
    response = flask.make_response("[Server]: " + error)
    response.status_code = 404
    return set_cors_headers(response)


class Tarasp:
    app = Flask(__name__)
    CORS(app)
    socketio = SocketIO(app, cors_allowed_origins='*')

    COMPONENT_TREE = []

    CURRENT_CAMERA_STATE = {}

    BASE_URL = 'http://127.0.0.1'
    PORT = 5000

    def __init__(self, port: int = 5000, output_path='./data/screenshots', print_component_tree=False):
        self.PORT = port
        BaseSceneElement.PORT = port
        self.app.config['SECRET_KEY'] = secrets.token_hex(16)

        Tarasp.app.config['UPLOAD_FOLDER'] = output_path
        self.print_component_tree = print_component_tree

        self._POINT_CLOUDS: [PotreePointCloud] = []
        self._POTREE_POINT_CLOUDS: [DefaultPointCloud] = []
        self._LINE_SETS: [LineSet] = []
        self._CAMERA_TRAJECTORIES: [CameraTrajectory] = []
        self._GROUPS: [Group] = []

    def run(self):
        # 1. Convert SceneElements to source
        self.convert_scene_elements()

        # 2. Turn object tree into a json-component tree
        self.create_component_tree()

        # 3. Run the application. Open browser by default?
        if self.print_component_tree:
            print(json.dumps(self.COMPONENT_TREE[0], indent=2))

        # Replace the Port number in the index.html to change it in the front-end
        self.replace_front_end_settings()

        print("[Server]: Starting server at " + self.BASE_URL + ":" + str(self.PORT))
        self.socketio.run(self.app, port=self.PORT)

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

            viewer = Viewer(scene_id)
            for pc in self._POINT_CLOUDS:
                viewer.add_element(pc)
            self.update_groups(self._POINT_CLOUDS)

            for ppc in self._POTREE_POINT_CLOUDS:
                viewer.add_element(ppc)
            self.update_groups(self._POTREE_POINT_CLOUDS)

            for ls in self._LINE_SETS:
                viewer.add_element(ls)
            self.update_groups(self._LINE_SETS)

            for ct in self._CAMERA_TRAJECTORIES:
                viewer.add_element(ct)
            self.update_groups(self._CAMERA_TRAJECTORIES)

            # The front-end uses (so far) an array to store the elements which are accessed via element_id
            # To not mix up objects and references, we sort them here
            viewer.elements.sort(key=lambda x: x.element_id, reverse=False)

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

    used_names = {}

    def update_groups(self, elements: List[BaseSceneElement]):

        # Real ugly way to check if different scene elements have the same name.
        # ----
        type_key = "unknown"
        if len(elements) > 0:
            type_key = str(type(elements[0]))
        for element in elements:
            name_as_key = json.dumps(element.name)
            if name_as_key in self.used_names.keys():
                if self.used_names[name_as_key] != type_key:
                    raise Exception(f"Trying to group different types together: {type_key}"
                                    f" and {self.used_names[name_as_key]}")
            else:
                self.used_names[name_as_key] = type_key

            # ------
            # Grouping continues here.
            element_id = element.element_id
            selected_group = Group("Unknown")
            current_groups = self._GROUPS
            for name in element.name:  # element.name is a list of strings. e.g. ["dir1", "dir2", "name"]
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

    # Why use regex instead of a template variable?
    # 1) Template variables can only be inserted in non-script tags but there would be a work around.
    # 2) When using a template variable, the index.html changes. That means that every time the front-end gets built,
    #    this has to be inserted again or automated somehow as Angular cannot deal with these template variables.
    # 3) The index.html is quite small. This shouldn't have a big performance impact.
    def replace_front_end_settings(self):
        # open index.html
        file = open('./front-end/index.html').read()

        # get the strings you want to swap
        # we get a list of all occurrences and then a tuple. So we extract the first element twice.
        settings_content = re.findall(r'(window\[\'port\'\] = (\d\d\d\d))', file)[0][0]
        new_content = f'window[\'port\'] = {self.PORT}'

        # replace
        replaced = file.replace(settings_content, new_content)

        # output string to new file
        file = open('./front-end/index.html', 'w')
        file.write(replaced)
        file.close()

    # ----------------------
    # REST-API
    # ----------------------

    @staticmethod
    @app.route('/')
    def func():
        response = flask.send_from_directory(directory='../../front-end/', path='index.html')
        return set_cors_headers(response)

    @staticmethod
    @app.route('/<path:file_name>')
    def serve_front_end(file_name):
        response = flask.send_from_directory(directory='../../front-end/', path=file_name)
        return set_cors_headers(response)

    # Handle all data calls by returning it as octet-stream.
    @staticmethod
    @app.route('/data/<path:file_name>')
    def serve_data(file_name):
        # TODO: check if its possible to serve any image on the disk: worked for " directory='/home/silas/Downloads/' "
        if not exists('data/' + file_name):
            return create_404_response("File not found: " + file_name)
        response = flask.send_from_directory(directory='../../data/', path=file_name, as_attachment=True)
        response.headers.set('Content-Type', 'application/octet-stream')
        return set_cors_headers(response)

    # Get the defined component-tree
    @staticmethod
    @app.route('/component_tree/<path:scene_id>')
    def get_component_tree(scene_id):
        scene_id = int(scene_id)
        if len(Tarasp.COMPONENT_TREE) < scene_id:
            return create_404_response("Error: No component tree found with the provided ID")
        else:
            response = flask.make_response(flask.jsonify(Tarasp.COMPONENT_TREE[scene_id]))
            response.status_code = 200
            return set_cors_headers(response)

    @staticmethod
    @app.route('/upload/<path:location>', methods=['POST', 'OPTIONS'])
    @cross_origin()
    def upload_file(location):
        # Some browsers send an OPTIONS request. Here we ack it
        if request.method == 'OPTIONS':
            response = flask.make_response("Options supported.")
            response.status_code = 200
            return response
        # check if the post request has the file part
        if 'file' not in request.files:
            response = flask.make_response("[Server]: No file provided")
            response.status_code = 404
            return response
        file = request.files['file']

        if file:
            save_path = os.path.join(Tarasp.app.config['UPLOAD_FOLDER'], location)
            if not exists(save_path):
                Path(save_path).mkdir(parents=True)
            # TODO: new naming concept, here we simply the current time in ms.
            file.save(os.path.join(save_path, str(time.time()) + '.png'))
            response = flask.make_response("Upload successful.")
            response.status_code = 200
            return response
        else:
            response = flask.make_response("Upload failed.")
            response.status_code = 200
            return response

    # SocketIO

    ANIMATION = {}

    def add_animation(self, func: Callable[[int], Union[CameraState, None]],
                      animation_name: str = "animation_1",
                      screenshot: bool = False,
                      screenshot_directory: str = '',
                      sleep_duration: float = 0.08):

        self.ANIMATION[animation_name] = {
            "function": func,
            "screenshot": screenshot,
            "screenshotDirectory": screenshot_directory,
            "sleep": sleep_duration
        }

    animation_thread = None
    animation_thread_lock = threading.Lock()

    @staticmethod
    @socketio.on('start_animation')
    def start_animation(data):
        data = json.loads(data)
        animation_name = data['animationName']
        scene_id = int(data['sceneId'])
        running = bool(data['running'])

        if animation_name not in Tarasp.ANIMATION.keys():
            print("[Server]: Error, no animation found with name " + animation_name)
            return

        print("[Server]: Starting animation for sceneId " + str(scene_id))

        def send_animation_update():
            animation = Tarasp.ANIMATION[animation_name]
            sleep_duration = animation['sleep']
            animation_data = {
                'screenshot': animation['screenshot'],
                'screenshotDirectory': animation['screenshotDirectory']
            }

            i = 0
            while True:
                if not running:  # TODO make it update the variable somehow?
                    break
                cam = animation['function'](i)
                if cam is None:
                    break
                else:
                    cam = cam.to_json()

                animation_data['cameraState'] = cam

                Tarasp.socketio.emit('animation', animation_data, broadcast=False)  # only send to originating user
                Tarasp.socketio.sleep(sleep_duration)
                i += 1
            with Tarasp.animation_thread_lock:
                Tarasp.animation_thread = None

        with Tarasp.animation_thread_lock:
            if Tarasp.animation_thread is None:
                Tarasp.animation_thread = Tarasp.socketio.start_background_task(target=send_animation_update)

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
