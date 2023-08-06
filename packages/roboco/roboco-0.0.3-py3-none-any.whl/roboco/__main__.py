#!/usr/bin/env python3
# ruff: noqa: T201
import argparse
import os
import sys

from InquirerPy import get_style, inquirer
from InquirerPy.base.control import Choice
from InquirerPy.utils import color_print

from roboco import __version__
from roboco.configurations import ProjectConfiguration, hardware_options, robots
from roboco.template import generate_from_template

green = "#00ffa1"
red = "#ff5858"
yellow = "#e5e512"
blue = "#61afef"
style = get_style(
    {"input": blue, "questionmark": yellow, "answermark": f"{green} bold"},
    style_override=False,
)
tick = "\u2714"

# This template makes heavy use of https://inquirerpy.readthedocs.io/en/latest/


def main():
    parser = argparse.ArgumentParser(description="Create a container for your robotics project")
    parser.add_argument("-V", "--version", action="store_true", default=False, help="display version")
    args = parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit()

    if os.path.exists("run.py") or os.path.exists("Dockerfile"):
        warn_message = "Warning: run.py and/or Dockerfile already exist(s) in this directory."
        color_print([(yellow, warn_message)])
        overwrite_message = "Overwrite these files and continue?"
        overwrite = inquirer.confirm(message=overwrite_message, default=False, style=style, amark=tick).execute()
        if not overwrite:
            print("Operation cancelled.")
            sys.exit()

    name = inquirer.text(message="Project name:", style=style, amark=tick).execute()
    min_container_name_length = 2  # minimum length allowed by docker
    if not name or len(name) < min_container_name_length:
        error_message = f"Error: Please enter a non-empty name, of at least {min_container_name_length} characters."
        color_print([(red, error_message)])
        sys.exit()

    robot_choice_key: str = inquirer.select(
        message="Choose your robot:",
        choices=[Choice(robot.key, robot.name) for robot in robots.values()],
        style=style,
        amark=tick,
    ).execute()
    robot_choice = robots[robot_choice_key]

    ros_distro = inquirer.select(
        "ROS version:", choices=robot_choice.compatible_ros_distros, style=style, amark=tick
    ).execute()

    hardware = []

    if len(robot_choice.compatible_hardware) > 0:
        possible_hardware_options = [
            Choice(hardware_option.key, hardware_option.name) for hardware_option in robot_choice.compatible_hardware
        ]
        hardware_keys = inquirer.checkbox(
            "Additional hardware:",
            instruction="(space to toggle selection)",
            choices=possible_hardware_options,
            style=style,
            amark=tick,
        ).execute()
        incompatible_hardware = False
        for hardware_key in hardware_keys:
            hardware_choice = hardware_options[hardware_key]
            if ros_distro not in hardware_choice.compatible_ros_distros:
                incompatible_hardware = True
                error_message = f"Error: {hardware_choice.name} is not compatible with ROS {ros_distro}."
                color_print([(red, error_message)])
                print("Please choose a different ROS version or remove this hardware option and try again.")
        if incompatible_hardware:
            sys.exit()
        hardware = [hardware_options[hardware_key] for hardware_key in hardware_keys]

    confirm = inquirer.confirm(message="Create project?", default=True, style=style, amark=tick).execute()

    if not confirm:
        print("Cancelled.")
        sys.exit()

    configuration = ProjectConfiguration(name, robot_choice, ros_distro, hardware)

    print("\nCreating project...")

    generate_from_template(configuration)

    color_print([(green, "\nDone. "), ("", "Now run:")])
    print(
        f"""
        cd {name}
        ./run.py
    """
    )


if __name__ == "__main__":
    main()
