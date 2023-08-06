from dataclasses import dataclass
from typing import Literal

ROSDistro = Literal["kinetic", "melodic", "noetic", "foxy", "galactic", "humble"]


@dataclass
class HardwareOption:
    key: str  # a unique identifier for the hardware option
    name: str
    compatible_ros_distros: list[ROSDistro]


@dataclass
class Robot:
    key: str  # a unique identifier for the robot type
    name: str
    compatible_ros_distros: list[ROSDistro]
    compatible_hardware: list[HardwareOption]


@dataclass
class ProjectConfiguration:
    name: str
    robot: Robot
    ros_distro: ROSDistro
    hardware: list[HardwareOption]


realsense_camera = HardwareOption("realsense_camera", "RealSense Camera", ["melodic", "noetic", "foxy", "humble"])
robotiq_2f85_gripper = HardwareOption("robotiq_2f85_gripper", "Robotiq 2F-85 Gripper", ["melodic", "noetic"])
robotiq_ft300_forcetorque = HardwareOption(
    "robotiq_ft300_forcetorque", "Robotiq FT-300 Force-Torque Sensor", ["melodic", "noetic"]
)
papillarray = HardwareOption("papillarray", "Contactile Papillarray Tactile Sensor", ["melodic", "noetic"])


abb_yumi = Robot("abb_yumi", "ABB YuMi", ["melodic", "noetic"], [])
baxter = Robot("baxter", "Baxter", ["kinetic", "noetic"], [])
fetch = Robot("fetch", "Fetch", ["melodic", "noetic"], [])
jackal = Robot("jackal", "Jackal", ["noetic", "foxy", "humble"], [realsense_camera])
panda = Robot("panda", "Panda", ["melodic", "noetic"], [realsense_camera])
ridgeback = Robot("ridgeback", "Ridgeback", ["noetic"], [])
ur5 = Robot(
    "ur5",
    "UR5",
    ["melodic", "noetic", "humble"],
    [realsense_camera, robotiq_2f85_gripper, robotiq_ft300_forcetorque, papillarray],
)
other = Robot("ros", "Other/None", ["kinetic", "melodic", "noetic", "foxy", "galactic", "humble"], [])

robots = {
    "abb_yumi": abb_yumi,
    "baxter": baxter,
    "fetch": fetch,
    "jackal": jackal,
    "panda": panda,
    "ridgeback": ridgeback,
    "ur5": ur5,
    "ros": other,
}

hardware_options = {
    "realsense_camera": realsense_camera,
    "robotiq_2f85_gripper": robotiq_2f85_gripper,
    "robotiq_ft300_forcetorque": robotiq_ft300_forcetorque,
    "papillarray": papillarray,
}
