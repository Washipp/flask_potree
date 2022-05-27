import flask
from flask import Flask, request

app = Flask(__name__)

COMPONENT_TREE = []

CURRENT_CAMERA_STATE = {}


def set_cors_headers(response: flask.Response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@app.route('/')  # defining a route in the application
def func():  # writing a function to be executed
    return app.root_path


@app.route('/data/<path:file_name>')
def serve_data(file_name):
    response = flask.send_from_directory(app.root_path + '/data/', file_name, as_attachment=True)
    response.headers.set('Content-Type', 'application/octet-stream')
    return set_cors_headers(response)


@app.route('/component-tree/<path:tree_id>')
def get_component_tree(tree_id):
    tree_id = int(tree_id)
    if len(COMPONENT_TREE) < tree_id:
        response = flask.make_response("Error: No component tree found with the provided ID")
        response.status_code = 404
        return set_cors_headers(response)
    else:
        response = flask.make_response(flask.jsonify(COMPONENT_TREE[tree_id]))
        response.status_code = 200
        return set_cors_headers(response)


@app.route('/camera_state/<int:scene_id>', methods=['GET', 'POST', 'OPTIONS'])
def camera_state(scene_id):
    if request.method == 'OPTIONS':
        response = flask.make_response("Options supported")
        response.status_code = 200
        return set_cors_headers(response)
    elif request.method == 'GET':
        if scene_id in CURRENT_CAMERA_STATE:
            response = flask.make_response(flask.jsonify(CURRENT_CAMERA_STATE[scene_id]))
            response.status_code = 200
            return set_cors_headers(response)
        else:
            response = flask.make_response("Error: No camera state found with the provided scene ID")
            response.status_code = 404
            return set_cors_headers(response)
    elif request.method == 'POST':
        CURRENT_CAMERA_STATE[scene_id] = request.form['state']
        response = flask.make_response("Camera State updated")
        response.status_code = 200
        return set_cors_headers(response)
    else:
        response = flask.make_response("Method not recognized")
        response.status_code = 501
        return set_cors_headers(response)


def load_camera_state():
    CURRENT_CAMERA_STATE[0] = {
        "position": {
            "x": 38.25590670544343,
            "y": 34.8853869591281,
            "z": 31.929537717547742
        },
        "rotation": {
            "_x": -0.8296086926953281,
            "_y": 0.6801674658568955,
            "_z": 0.6020464180012758,
            "_order": "XYZ"
        },
        "fov": 45,
        "near": 0.1,
        "far": 1000,
        "lastUpdate": 1653462775419
    }


def load_tree():
    tree = [
        {
            "component": "row",
            "data":
                {"id": 0, },
            "children": [
                {
                    "component": "col",
                    "data":
                        {
                            "id": 1,
                            "width": 3,
                        },
                    "children": [
                        {
                            "component": "general_settings",
                            "data":
                                {
                                    "sceneId": 0,
                                },
                            "children": [],
                        },
                        {
                            "component": "element_tree",
                            "data": {
                                "sceneId": 0,
                            },
                            "children": [],
                        },
                        {
                            "component": "element_settings",
                            "data":
                                {
                                    "sceneId": 0,
                                    "elementId": 0,
                                },
                            "children": [],
                        },
                        {
                            "component": "element_settings",
                            "data":
                                {
                                    "sceneId": 0,
                                    "elementId": 1,
                                },
                            "children": [],
                        }
                    ],
                },
                {
                    "component": "col",
                    "data":
                        {
                            "id": 2,
                            "width": 9,
                        },
                    "children": [
                        {
                            "component": "viewer",
                            "data": {
                                "sceneId": 0,
                                "elements": [
                                    {
                                        "elementId": 0,
                                        "source": "http://127.0.0.1:5000/data/lion_takanawa/",
                                        "sceneType": "potree_point_cloud",
                                        "attributes": {
                                            "name": "Lion 1",
                                            "material": {
                                                "size": 2,
                                            },
                                            "position": {
                                                "x": 15,
                                                "y": 0,
                                                "z": 0,
                                            },
                                            "scale": {
                                                "x": 10,
                                                "y": 10,
                                                "z": 10,
                                            }
                                        },
                                    },
                                    {
                                        "elementId": 1,
                                        "source": "http://127.0.0.1:5000/data/lion_takanawa/",
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
                                            },
                                            "scale": {
                                                "x": 10,
                                                "y": 10,
                                                "z": 10,
                                            }
                                        },
                                    },
                                    {
                                        "elementId": 2,
                                        "source":
                                            [
                                                {
                                                    "start": {
                                                        "x": -10,
                                                        "y": -5,
                                                        "z": 0
                                                    },
                                                    "end": {
                                                        "x": -10,
                                                        "y": 5,
                                                        "z": 0
                                                    }
                                                }, {
                                                    "start": {
                                                        "x": -10,
                                                        "y": 5,
                                                        "z": 0
                                                    },
                                                    "end": {
                                                        "x": 10,
                                                        "y": 5,
                                                        "z": 0
                                                    }
                                                }, {
                                                    "start": {
                                                        "x": 10,
                                                        "y": 5,
                                                        "z": 0
                                                    },
                                                    "end": {
                                                        "x": 10,
                                                        "y": -5,
                                                        "z": 0
                                                    }
                                                }, {
                                                    "start": {
                                                        "x": 10,
                                                        "y": -5,
                                                        "z": 0
                                                    },
                                                    "end": {
                                                        "x": -10,
                                                        "y": -5,
                                                        "z": 0
                                                    }
                                                },
                                            ],
                                        "sceneType": "line_set",
                                        "attributes": {
                                            "name": "Line Set 1",
                                            "material": {
                                                "color": "0x0000ff",
                                            }
                                        },
                                    },
                                    {
                                        "elementId": 3,
                                        "source":
                                            {
                                                "x": {
                                                    "x": 1,
                                                    "y": 1,
                                                    "z": 1
                                                },

                                                "y1": {
                                                    "x": -3,
                                                    "y": 2,
                                                    "z": 10
                                                },

                                                "y2": {
                                                    "x": 3,
                                                    "y": 2,
                                                    "z": 10
                                                },

                                                "y3": {
                                                    "x": 3,
                                                    "y": -2,
                                                    "z": 10
                                                },

                                                "y4": {
                                                    "x": -3,
                                                    "y": -2,
                                                    "z": 10
                                                }
                                            },
                                        "sceneType": "camera_trajectory",
                                        "attributes": {
                                            "name": "Camera Frustum",
                                            "material": {
                                                "color": "00ff00",
                                            }
                                        },
                                     }
                                ]
                            },
                            "children": [],
                        }
                    ],
                },
            ],
        }
    ]
    COMPONENT_TREE.append(tree)


if __name__ == '__main__':  # calling  main
    load_tree()
    load_camera_state()
    app.debug = True  # setting the debugging option for the application instance
    app.run()  # launching the flask's integrated development webserver
