
# Robot Containers
This repository contains Dockerfiles for building containers for [various robots](#available-containers).
It also includes a python script `run.py` that wraps the `docker` command to enable:

- building, starting and entering the container in one step
- graphical applications
- nvidia GPU passthrough
- realtime scheduling
- host networking
- full external device access (USB, cameras, etc.)

Finally, it includes `roboco`, a script for generating a new project from the included Dockerfiles.

[![CI - Test](https://github.com/monashrobotics/robot_containers/actions/workflows/test.yml/badge.svg)](https://github.com/monashrobotics/robot_containers/actions/workflows/test.yml)
[![CI - Docker Images](https://github.com/monashrobotics/robot_containers/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/monashrobotics/robot_containers/actions/workflows/docker-publish.yml)
[![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff) [![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

## Table of Contents

  * [Requirements](#requirements)
  * [Installation](#installation)
  * [Usage](#usage)
    * [Creating a new project](#creating-a-new-project)
    * [Running the container](#running-the-container)
    * [Customising the container](#customising-the-container)
* [Available containers](#available-containers)

## Requirements

### Docker
- Tested with Docker 20.10.23. 

- Install on Ubuntu using `sudo apt install docker.io` (other installation methods may not play well with the nvidia-docker2 runtime.)

- Follow "Manage Docker as a non-root user" at https://docs.docker.com/engine/install/linux-postinstall/

### nvidia-docker2 (for GPU support, optional)
- Install nvidia-docker2 by following https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#setting-up-nvidia-container-toolkit

### VSCode - Dev Containers Extension (Optional)
- Tested with v0.292.0 of Dev Containers extension https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers

## Installation

### Using pip
```
pip install roboco
```

### Using git
```
git clone https://github.com/monashrobotics/robot_containers.git
cd robot_containers
pip install .
```

## Usage
### Creating a new project
```
roboco init
```

Follow the prompts to select the robot type and additional features.

Once completed, there will be two new files in your current directory: `Dockerfile` and `run.py`.

### Running the container

Build the image and run the container using:
```
./run.py
```

### Customising the container

The `Dockerfile` can be edited to add additional dependencies or change the base image.

When you make changes to the `Dockerfile`, you will need to rebuild the image using:
```
./run.py build
```
Then remove the old container and start a new one:
```
./run.py rm
./run.py
```

## Available Containers

| Robot / ROS Distro (Ubuntu OS) | ROS 1 Melodic (18.04) | ROS 1 Noetic (20.04) | ROS 2 Foxy (20.04) | ROS 2 Humble (22.04)
| --- | :---: | :---: | :---: | :---: |
| ABB YuMi | ✅ | ✅ | ❌ | ❌ |
| Baxter | ❌ | ✅ | ❌ | ❌ |
| Fetch | ❌ | ✅ | ❌ | ❌ |
| Jackal | ❌ | ✅ | ✅ | ✅ |
| Panda | ❌ | ✅ | ❌ | ❌ |
| Ridgeback | ❌ | ✅ | ❌ | ❌ |
| UR5 | ❌ | ✅ | ❌ | ✅ |

| Driver / ROS Distro (Ubuntu OS) | ROS 1 Melodic (18.04) | ROS 1 Noetic (20.04) | ROS 2 Foxy (20.04) | ROS 2 Humble (22.04)
| --- | :---: | :---: | :---: | :---: |
| RealSense Camera | ✅ | ✅ | ✅ | ✅ |
| Velodyne LiDAR | ✅ | ✅ | ✅ | ✅ |
| Robotiq 2F-85 Gripper | ✅ | ✅ | ❌ | ❌ |
| Robotiq FT-300 Force-Torque Sensor | ✅ | ✅ | ❌ | ❌ |
