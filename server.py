import flask
from flask import Flask

app = Flask(__name__)

COMPONENT_TREE = []


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
                                "pcos": [
                                    {
                                        "elementId": 0,
                                        "url": "http://127.0.0.1:5000/data/lion_takanawa/",
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
                                        "url": "http://127.0.0.1:5000/data/lion_takanawa/",
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
    app.debug = True  # setting the debugging option for the application instance
    app.run()  # launching the flask's integrated development webserver
