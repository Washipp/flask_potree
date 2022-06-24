# Potree-Viewer Back-End

## Prerequisites

Install the following tools:

* [Colmap](https://colmap.github.io/)
  * Installing it when conda is activated creates problems. See this [thread](https://github.com/colmap/colmap/issues/188) for possible solutions.
* See `requirements.txt` for the needed python packages.
* [PotreeConverter v1.6](https://github.com/potree/PotreeConverter/releases/tag/1.6). Do not use a newer version! Add the `PotreeConverter` to `./converter`


## Installation

Clone the repository. It is not yet a python package so classes/methods need to be imported locally. 

E.g. `from src.SceneElements.elements import PotreePointCloud`

See `example.py` for usage.

The front-end is already built and located in `front-end`. The project is located [here](https://github.com/Washipp/ts-potree) with its own README.md.

### Create the following directories:

* data
* data/converted

### elements.py

Depending on the OS the command to convert plyfile to potree format changes. In `elements.py` in the function `ply_to_potree` adapt it accordingly.

## Missing Features / Known Issues

* Paths
  * Paths linking to the directory might be different on other OS. This has only been tested on Linux
  * Output directory might need to be added manually.
* The Port cannot be changed at this point. It used 5000 as default.
  * Why? As the front-end build is already done, we cannot change it in the code. So we could create a service that loads the port from this application. But the way that the lifecycle hooks work in angular make this quite difficult.
