import json

import flask
from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins='*')

COMPONENT_TREE = []


# REST-API to get the data


# Allow all accesses by default.
def set_cors_headers(response: flask.Response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@app.route('/')
def func():
    return app.root_path


# Handle all data calls by returning it as octet-stream.
@app.route('/data/<path:file_name>')
def serve_data(file_name):
    response = flask.send_from_directory(app.root_path + '/data/', file_name, as_attachment=True)
    response.headers.set('Content-Type', 'application/octet-stream')
    return set_cors_headers(response)


# Get the defined component-tree
@app.route('/component_tree/<path:tree_id>')
def get_component_tree(tree_id):
    tree_id = int(tree_id)
    if len(COMPONENT_TREE) < tree_id:
        response = flask.make_response("[Server]: Error: No component tree found with the provided ID")
        response.status_code = 404
        return set_cors_headers(response)
    else:
        response = flask.make_response(flask.jsonify(COMPONENT_TREE[tree_id]))
        response.status_code = 200
        return set_cors_headers(response)


@app.route('/get_update/')
def get_update():
    update = [
        [0, 1, 0],
        ['camera', 'position'],
        {
            "x": 10,
            "y": 10,
            "z": 10,
        }
    ]
    response = flask.make_response(flask.jsonify(update))
    response.status_code = 200
    return set_cors_headers(response)


# SocketIO

CURRENT_CAMERA_STATE = {}


@socketio.on('json')
def test_message(message):
    data = json.loads(message)
    scene_id = data['sceneId']
    state = data['state']
    if len(CURRENT_CAMERA_STATE) == 0:
        CURRENT_CAMERA_STATE[scene_id] = state
    else:
        last_update = CURRENT_CAMERA_STATE[scene_id]['lastUpdate']

        if last_update + 30 < state['lastUpdate']:
            CURRENT_CAMERA_STATE[scene_id] = state
            emit('json', state, broadcast=True, include_self=False)


@socketio.on('connect')
def test_connect():
    print('Client connected')


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


def load_tree():
    tree = [
        {
            "component": "row",
            "componentId": 0,
            "data":
                {},
            "children": [
                {
                    "component": "col",
                    "componentId": 0,
                    "data":
                        {
                            "width": 3,
                        },
                    "children": [
                        {
                            "component": "general_settings",
                            "componentId": 0,
                            "data":
                                {
                                    "sceneId": 0,
                                },
                            "children": [],
                        },
                        {
                            "component": "element_tree",
                            "componentId": 1,
                            "data": {
                                "sceneId": 0,
                                "groups": [
                                    {
                                        "groupId": 0,
                                        "name": "Group 1",
                                        "ids": [2, 3, 5, 6],
                                        "groups": [],
                                        "visible": True,
                                    },
                                    {
                                        "groupId": 1,
                                        "name": "All Point-Clouds",
                                        "ids": [],
                                        "groups": [
                                            {
                                                "groupId": 2,
                                                "name": "PointCloud Set 1",
                                                "ids": [0, 1],
                                                "groups": [],
                                                "visible": True,
                                            },
                                            {
                                                "groupId": 3,
                                                "name": "PointCloud Set 2",
                                                "ids": [4],
                                                "groups": [],
                                                "visible": True,
                                            },
                                        ],
                                        "visible": True,
                                    },

                                ],
                            },
                            "children": [],
                        }, ],
                },
                {
                    "component": "col",
                    "componentId": 1,
                    "data":
                        {
                            "width": 9,
                        },
                    "children": [
                        {
                            "component": "viewer",
                            "componentId": 0,
                            "data": {
                                "sceneId": 0,
                                "camera": {
                                    "position": [ 138.25590670544343,134.8853869591281,131.929537717547742
                                    ],
                                    "rotation": [ -0.8296086926953281,0.6801674658568955,0.6020464180012758,
                                    ],
                                    "fov": 90,
                                    "near": 0.1,
                                    "far": 100000000,
                                },
                                "elements": [
                                    {
                                        "elementId": 0,
                                        "sceneType": "potree_point_cloud",
                                        "attributes": {
                                            "name": "ETH - CAB",
                                            "material": {
                                                "size": 2,
                                            },
                                            "position": {
                                                "x": 15,
                                                "y": 0,
                                                "z": 0,
                                            }
                                        },
                                        "source": "http://127.0.0.1:5000/data/mesh_simplified_converted/",
                                    },
                                    {
                                        "elementId": 1,
                                        "sceneType": "potree_point_cloud",
                                        "attributes": {
                                            "name": "Lion 2",
                                            "material": {
                                                "size": 2,
                                            },
                                            "position": {
                                                "x": -15,
                                                "y": 0,
                                                "z": 0,
                                            }
                                        },
                                        "source": "http://127.0.0.1:5000/data/lion_takanawa/",
                                    },
                                    {
                                        "elementId": 2,
                                        "sceneType": "line_set",
                                        "attributes": {
                                            "name": "Line Set 1",
                                            "material": {
                                                "color": "#0000ff",
                                            }
                                        },
                                        "source":
                                            [
                                                [[-10, -5, 0], [-10, 5, 0], ],
                                                [[-10, 5, 0], [10, 5, 0], ],
                                                [[-10, 5, 0], [10, 5, 0], ],
                                                [[10, 5, 0], [10, -5, 0], ],
                                                [[10, -5, 0], [-10, -5, 0], ],
                                            ],
                                    },
                                    {
                                        "elementId": 3,
                                        "sceneType": "camera_trajectory",
                                        "attributes": {
                                            "name": "Camera Frustum",
                                            "material": {
                                                "color": "#00ff00",
                                            },
                                            "imageUrl": "http://127.0.0.1:5000/data/images/03903474_1471484089.jpg",
                                        },
                                        "source":
                                            {
                                                "t": [5, 5, 5],
                                                "r": [2, 2, 2, 0],
                                            },
                                    },
                                    {
                                        "elementId": 4,
                                        "sceneType": "default_point_cloud",
                                        "attributes": {
                                            "name": "Fragment Point Cloud",
                                            "material": {
                                                "size": 5,
                                            },
                                        },
                                        "source": "http://127.0.0.1:5000/data/fragment.ply",
                                    },
                                    {
                                        "elementId": 5,
                                        "sceneType": "camera_trajectory",
                                        "attributes": {
                                            "name": "Camera Frustum",
                                            "material": {
                                                "color": "#0000ff",
                                            },
                                            "imageUrl": "http://127.0.0.1:5000/data/images/03903474_1471484089.jpg",
                                        },
                                        "source":
                                            {
                                                "t": [10, 10, 10],
                                                "r": [0, 0, 0, 0],
                                            },
                                    },
                                    {
                                        "elementId": 6,
                                        "sceneType": "camera_trajectory",
                                        "attributes": {
                                            "name": "Camera Frustum",
                                            "material": {
                                                "color": "#ff0000",
                                            },
                                            "imageUrl": "http://127.0.0.1:5000/data/images/03903474_1471484089.jpg",
                                        },
                                        "source":
                                            {
                                                "t": [15, 15, 15],
                                                "r": [1, 1, 1, 0],
                                            },
                                    },
                                ],
                            },
                            "children": [],
                        }, ],
                }, ],
        }
    ]
    COMPONENT_TREE.append(tree)


if __name__ == '__main__':  # calling  main
    load_tree()
    # app.debug = True  # setting the debugging option for the application instance
    # app.run()
    socketio.run(app)
